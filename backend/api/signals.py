from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import ChatRoom, Match
import logging

logger = logging.getLogger(__name__)

@receiver(post_delete, sender=Match)
def cleanup_orphaned_chat_rooms(sender, instance, **kwargs):
    try:
        if instance.chat_room and not Match.objects.filter(chat_room=instance.chat_room).exists():
            instance.chat_room.delete()
    except Exception as e:
        logger.error(f"Error cleaning up chat room: {str(e)}")
