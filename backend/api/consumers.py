import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
import secrets

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.user = self.scope['user']
        self.room_group_name = f'chat_{self.room_id}'
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        has_access = await self._verify_access()
        if not has_access:
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        other_user = await self._get_other_user()
        if other_user:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'user': self.user.anonymous_handle,
                }
            )
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        await self._remove_typing_indicator()
        
        other_user = await self._get_other_user()
        if other_user:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user': self.user.anonymous_handle,
                }
            )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'error': 'Invalid JSON'}))
            return
        
        message_type = data.get('type')
        
        if message_type == 'message':
            await self._handle_message(data)
        elif message_type == 'typing':
            await self._handle_typing(data)
        elif message_type == 'seen':
            await self._handle_seen(data)
        else:
            await self.send(text_data=json.dumps({'error': 'Unknown message type'}))
    
    async def _handle_message(self, data):
        msg_type = data.get('message_type', 'text')
        content = data.get('content', '')
        media_url = data.get('media_url', '')
        
        if not content and not media_url:
            await self.send(text_data=json.dumps({'error': 'Empty message'}))
            return
        
        is_locked = await self._check_locked()
        if is_locked:
            await self.send(text_data=json.dumps({'error': 'Chat room is locked'}))
            return
        
        message = await self._save_message(msg_type, content, media_url)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': str(message.id),
                'sender': self.user.anonymous_handle,
                'message_type': msg_type,
                'content': content,
                'media_url': media_url,
                'timestamp': message.created_at.isoformat(),
            }
        )
        
        await self._remove_typing_indicator()
    
    async def _handle_typing(self, data):
        is_typing = data.get('is_typing', False)
        
        if is_typing:
            await self._add_typing_indicator()
        else:
            await self._remove_typing_indicator()
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user': self.user.anonymous_handle,
                'is_typing': is_typing,
            }
        )
    
    async def _handle_seen(self, data):
        message_id = data.get('message_id')
        
        await self._mark_seen(message_id)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message_seen',
                'message_id': message_id,
                'user': self.user.anonymous_handle,
            }
        )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'sender': event['sender'],
            'message_type': event['message_type'],
            'content': event['content'],
            'media_url': event['media_url'],
            'timestamp': event['timestamp'],
        }))
    
    async def typing_indicator(self, event):
        if event['user'] != self.user.anonymous_handle:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user': event['user'],
                'is_typing': event['is_typing'],
            }))
    
    async def message_seen(self, event):
        await self.send(text_data=json.dumps({
            'type': 'seen',
            'message_id': event['message_id'],
            'user': event['user'],
        }))
    
    async def user_joined(self, event):
        if event['user'] != self.user.anonymous_handle:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user': event['user'],
            }))
    
    async def user_left(self, event):
        if event['user'] != self.user.anonymous_handle:
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'user': event['user'],
            }))
    
    @database_sync_to_async
    def _verify_access(self):
        from .models import ChatRoom
        
        try:
            room = ChatRoom.objects.get(id=self.room_id, is_deleted=False)
            user = self.user
            
            if not (room.user_a == user or room.user_b == user):
                return False
            
            if room.is_locked:
                has_active_subscription = room.subscriptions.filter(
                    user=user,
                    status='success',
                    expires_at__gt=timezone.now()
                ).exists()
                if not has_active_subscription:
                    return False
            
            return True
        except:
            return False
    
    @database_sync_to_async
    def _get_other_user(self):
        from .models import ChatRoom
        
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            if room.user_a == self.user:
                return room.user_b
            else:
                return room.user_a
        except:
            return None
    
    @database_sync_to_async
    def _check_locked(self):
        from .models import ChatRoom
        
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            if room.is_locked:
                has_subscription = room.subscriptions.filter(
                    user=self.user,
                    status='success',
                    expires_at__gt=timezone.now()
                ).exists()
                return not has_subscription
            return False
        except:
            return True
    
    @database_sync_to_async
    def _save_message(self, msg_type, content, media_url):
        from .models import ChatMessage, ChatRoom
        
        room = ChatRoom.objects.get(id=self.room_id)
        message = ChatMessage.objects.create(
            room=room,
            sender=self.user,
            message_type=msg_type,
            content=content,
            media_url=media_url,
        )
        
        room.last_activity = timezone.now()
        room.save(update_fields=['last_activity'])
        
        return message
    
    @database_sync_to_async
    def _add_typing_indicator(self):
        from .models import TypingIndicator
        
        TypingIndicator.objects.update_or_create(
            room_id=self.room_id,
            user=self.user,
            defaults={'created_at': timezone.now()}
        )
    
    @database_sync_to_async
    def _remove_typing_indicator(self):
        from .models import TypingIndicator
        
        TypingIndicator.objects.filter(
            room_id=self.room_id,
            user=self.user
        ).delete()
    
    @database_sync_to_async
    def _mark_seen(self, message_id):
        from .models import ChatMessage
        
        try:
            message = ChatMessage.objects.get(id=message_id)
            if message.sender != self.user:
                message.is_seen = True
                message.seen_at = timezone.now()
                message.save(update_fields=['is_seen', 'seen_at'])
        except:
            pass
