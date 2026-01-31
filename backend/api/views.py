from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import timedelta
import logging

from .models import (
    User, EmailVerification, InstitutionDomain, MatchProfile, Match, ChatRoom,
    ChatMessage, Sticker, Gift, SentGift, Notification, AbuseReport, Subscription,
    TokenTransaction, TypingIndicator, PaymentReminder
)
from .serializers import (
    UserRegistrationSerializer, OTPVerificationSerializer, UserProfileSerializer,
    MatchProfileSerializer, MatchSerializer, ChatRoomSerializer, ChatMessageSerializer,
    StickerSerializer, GiftSerializer, SentGiftSerializer, NotificationSerializer,
    AdminUserListSerializer, TokenTransactionSerializer
)
from .tasks import send_otp_email
from .matching import MatchingEngine
from .admin_auth import AdminAuthentication

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user, otp = serializer.save()
        send_otp_email.delay(user.email, otp)
        return Response({
            'message': 'OTP sent to email',
            'email': user.email
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_otp(request):
    serializer = OTPVerificationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        verification = serializer.validated_data['verification']
        
        verification.is_verified = True
        verification.save(update_fields=['is_verified'])
        
        domain = user.email.split('@')[1].lower()
        is_institutional = InstitutionDomain.objects.filter(
            domain=domain, is_approved=True
        ).exists()
        
        if not is_institutional:
            approved_list = InstitutionDomain.objects.filter(is_approved=True).values_list('domain', flat=True)
            is_institutional = any(
                user.email.lower().endswith(f"@{approved}") 
                for approved in approved_list
            )
        
        user.is_verified = True
        user.is_institutional = is_institutional
        user.verified_at = timezone.now()
        user.save(update_fields=['is_verified', 'is_institutional', 'verified_at'])
        
        if not user.match_profile:
            MatchProfile.objects.create(user=user)
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def resend_otp(request):
    email = request.data.get('email', '').lower()
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if user.is_verified:
        return Response({'error': 'User already verified'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        verification = EmailVerification.objects.get(user=user)
        verification.delete()
    except:
        pass
    
    otp = ''.join(str(i) for i in range(6))
    expires_at = timezone.now() + timedelta(minutes=10)
    
    verification = EmailVerification.objects.create(
        user=user,
        email=email,
        otp=otp,
        expires_at=expires_at,
    )
    
    send_otp_email.delay(email, otp)
    return Response({'message': 'OTP resent'}, status=status.HTTP_200_OK)

class UserProfileViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        user = request.user
        return Response(UserProfileSerializer(user).data)
    
    def partial_update(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def update_match_preferences(self, request):
        user = request.user
        profile, created = MatchProfile.objects.get_or_create(user=user)
        
        serializer = MatchProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MatchingViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        user = request.user
        
        if not user.match_profile or not user.match_profile.is_active:
            return Response({'error': 'Match profile not configured'}, status=status.HTTP_400_BAD_REQUEST)
        
        engine = MatchingEngine()
        candidates = engine.find_candidates(user)
        
        serializer = MatchSerializer(candidates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_match(self, request):
        user = request.user
        target_id = request.data.get('target_user_id')
        
        try:
            target = User.objects.get(user_uuid=target_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not user.match_profile or not user.match_profile.is_active:
            return Response({'error': 'Match profile not configured'}, status=status.HTTP_400_BAD_REQUEST)
        
        engine = MatchingEngine()
        mode = request.data.get('mode', 'friend')
        
        if not engine.validate_mode(user, target, mode):
            return Response({'error': 'Invalid match request'}, status=status.HTTP_400_BAD_REQUEST)
        
        match, created = Match.objects.get_or_create(
            user_a=min([user, target], key=lambda u: str(u.id)),
            user_b=max([user, target], key=lambda u: str(u.id)),
            defaults={
                'mode': mode,
                'match_score': engine.calculate_score(user, target),
                'expires_at': timezone.now() + timedelta(days=30),
            }
        )
        
        if created:
            chat_room, _ = ChatRoom.objects.get_or_create(
                user_a=match.user_a,
                user_b=match.user_b,
                defaults={
                    'expires_at': timezone.now() + timedelta(days=7),
                }
            )
            match.chat_room = chat_room
            match.save(update_fields=['chat_room'])
            
            Notification.objects.create(
                user=target,
                notification_type='match',
                title='New Match!',
                body='You have a new match!',
            )
        
        return Response(MatchSerializer(match).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class ChatRoomViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        user = request.user
        rooms = ChatRoom.objects.filter(
            Q(user_a=user) | Q(user_b=user),
            is_deleted=False
        ).order_by('-last_activity')
        
        page_size = 20
        paginator = request.query_params.get('page', 1)
        offset = (int(paginator) - 1) * page_size
        
        rooms = rooms[offset:offset + page_size]
        serializer = ChatRoomSerializer(rooms, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        user = request.user
        try:
            room = ChatRoom.objects.get(
                id=pk,
                is_deleted=False
            )
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not (room.user_a == user or room.user_b == user):
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if room.is_locked and not room.subscriptions.filter(user=user, status='success').exists():
            return Response({'error': 'Chat room is locked'}, status=status.HTTP_403_FORBIDDEN)
        
        return Response(ChatRoomSerializer(room).data)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        user = request.user
        try:
            room = ChatRoom.objects.get(id=pk)
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not (room.user_a == user or room.user_b == user):
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if room.is_locked and not room.subscriptions.filter(user=user, status='success').exists():
            return Response({'error': 'Chat room is locked'}, status=status.HTTP_403_FORBIDDEN)
        
        page_size = 20
        page = int(request.query_params.get('page', 1))
        offset = (page - 1) * page_size
        
        messages = room.messages.filter(is_deleted=False).order_by('-created_at')[offset:offset + page_size]
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        user = request.user
        try:
            room = ChatRoom.objects.get(id=pk)
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not (room.user_a == user or room.user_b == user):
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if room.is_locked and not room.subscriptions.filter(user=user, status='success').exists():
            return Response({'error': 'Chat room is locked'}, status=status.HTTP_403_FORBIDDEN)
        
        message_type = request.data.get('message_type', 'text')
        content = request.data.get('content', '')
        media_url = request.data.get('media_url', '')
        
        message = ChatMessage.objects.create(
            room=room,
            sender=user,
            message_type=message_type,
            content=content,
            media_url=media_url,
        )
        
        room.save(update_fields=['last_activity'])
        
        return Response(ChatMessageSerializer(message).data, status=status.HTTP_201_CREATED)

class StickerViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Sticker.objects.filter(is_active=True)
    serializer_class = StickerSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Sticker.objects.filter(is_active=True)
        
        tier = self.request.query_params.get('tier')
        if tier:
            queryset = queryset.filter(tier=tier)
        
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset.order_by('tier', 'name')

class GiftViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Gift.objects.filter(is_active=True)
    serializer_class = GiftSerializer

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_gift(request):
    user = request.user
    gift_id = request.data.get('gift_id')
    recipient_uuid = request.data.get('recipient_uuid')
    room_id = request.data.get('room_id')
    message = request.data.get('message', '')
    
    try:
        gift = Gift.objects.get(id=gift_id, is_active=True)
        recipient = User.objects.get(user_uuid=recipient_uuid)
        room = ChatRoom.objects.get(id=room_id)
    except (Gift.DoesNotExist, User.DoesNotExist, ChatRoom.DoesNotExist):
        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
    
    if user.tokens_balance < gift.token_cost:
        return Response({'error': 'Insufficient tokens'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not (room.user_a == user or room.user_b == user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    user.tokens_balance -= gift.token_cost
    user.save(update_fields=['tokens_balance'])
    
    TokenTransaction.objects.create(
        user=user,
        transaction_type='gift',
        amount=-gift.token_cost,
        balance_before=user.tokens_balance + gift.token_cost,
        balance_after=user.tokens_balance,
        description=f'Gift: {gift.name}',
        related_object_id=str(gift.id),
    )
    
    sent_gift = SentGift.objects.create(
        gift=gift,
        sender=user,
        recipient=recipient,
        chat_room=room,
        message=message,
    )
    
    return Response(SentGiftSerializer(sent_gift).data, status=status.HTTP_201_CREATED)

class NotificationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        user = request.user
        notifications = Notification.objects.filter(user=user).order_by('-created_at')
        
        page_size = 20
        page = int(request.query_params.get('page', 1))
        offset = (page - 1) * page_size
        
        notifications = notifications[offset:offset + page_size]
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_as_read(self, request):
        user = request.user
        notification_id = request.data.get('notification_id')
        
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=['is_read', 'read_at'])
            return Response({'status': 'marked as read'})
        except Notification.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def dismiss(self, request):
        user = request.user
        notification_id = request.data.get('notification_id')
        
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.is_dismissed = True
            notification.dismissed_at = timezone.now()
            notification.save(update_fields=['is_dismissed', 'dismissed_at'])
            return Response({'status': 'dismissed'})
        except Notification.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def report_abuse(request):
    user = request.user
    reported_user_id = request.data.get('reported_user_id')
    reason = request.data.get('reason')
    evidence_urls = request.data.get('evidence_urls', [])
    
    try:
        reported_user = User.objects.get(user_uuid=reported_user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    existing = AbuseReport.objects.filter(
        reporter=user,
        reported_user=reported_user
    ).exists()
    
    if existing:
        return Response({'error': 'Already reported'}, status=status.HTTP_400_BAD_REQUEST)
    
    report = AbuseReport.objects.create(
        reporter=user,
        reported_user=reported_user,
        reason=reason,
        evidence_urls=evidence_urls,
    )
    
    return Response(
        {'message': 'Report submitted'},
        status=status.HTTP_201_CREATED
    )

class AdminViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def dispatch(self, request, *args, **kwargs):
        admin_auth = AdminAuthentication()
        if not admin_auth.is_admin(request.user):
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().dispatch(request, *args, **kwargs)
    
    def users_list(self, request):
        page_size = 50
        page = int(request.query_params.get('page', 1))
        offset = (page - 1) * page_size
        
        users = User.objects.all().order_by('-created_at')[offset:offset + page_size]
        serializer = AdminUserListSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def ban_user(self, request):
        user_id = request.data.get('user_id')
        reason = request.data.get('reason', '')
        
        try:
            user = User.objects.get(user_uuid=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user.is_banned = True
        user.banned_at = timezone.now()
        user.ban_reason = reason
        user.save(update_fields=['is_banned', 'banned_at', 'ban_reason'])
        
        return Response({'status': 'user banned'})
    
    @action(detail=False, methods=['post'])
    def delete_user(self, request):
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(user_uuid=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user.delete()
        return Response({'status': 'user deleted'})
