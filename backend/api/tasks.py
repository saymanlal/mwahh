from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .models import (
    ChatRoom, Notification, PaymentReminder, User, Subscription,
    EmailVerification, Match
)
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_otp_email(email, otp):
    try:
        send_mail(
            subject='Your Matchmaking Platform OTP',
            message=f'Your OTP is: {otp}\n\nValid for 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"OTP sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send OTP to {email}: {str(e)}")
        return False
    return True

@shared_task
def expire_chats():
    now = timezone.now()
    expired_chats = ChatRoom.objects.filter(
        expires_at__lte=now,
        is_locked=False,
        is_deleted=False
    )
    
    for chat in expired_chats:
        chat.is_locked = True
        chat.locked_at = now
        chat.save(update_fields=['is_locked', 'locked_at'])
        
        Notification.objects.create(
            user=chat.user_a,
            notification_type='chat_expiring',
            title='Chat Room Expired',
            body='Your chat room has expired. Pay to continue.',
            related_room_id=str(chat.id),
        )
        Notification.objects.create(
            user=chat.user_b,
            notification_type='chat_expiring',
            title='Chat Room Expired',
            body='Your chat room has expired. Pay to continue.',
            related_room_id=str(chat.id),
        )
    
    logger.info(f"Expired {expired_chats.count()} chat rooms")

@shared_task
def send_payment_reminders():
    now = timezone.now()
    five_days_from_now = now + timedelta(days=5)
    seven_days_from_now = now + timedelta(days=7)
    
    day_five_chats = ChatRoom.objects.filter(
        expires_at__lte=five_days_from_now,
        expires_at__gt=now,
        is_locked=False,
        is_deleted=False
    ).exclude(notifications__notification_type='payment_reminder')
    
    for chat in day_five_chats:
        Notification.objects.create(
            user=chat.user_a,
            notification_type='payment_reminder',
            title='Chat Expiring Soon',
            body='Your chat will expire in 2 days. Pay now to keep chatting.',
            related_room_id=str(chat.id),
        )
        Notification.objects.create(
            user=chat.user_b,
            notification_type='payment_reminder',
            title='Chat Expiring Soon',
            body='Your chat will expire in 2 days. Pay now to keep chatting.',
            related_room_id=str(chat.id),
        )
    
    logger.info(f"Sent payment reminders for {day_five_chats.count()} chats")

@shared_task
def cleanup_expired_otps():
    now = timezone.now()
    expired = EmailVerification.objects.filter(expires_at__lt=now, is_verified=False)
    count = expired.count()
    expired.delete()
    logger.info(f"Cleaned up {count} expired OTPs")

@shared_task
def cleanup_unverified_users():
    week_ago = timezone.now() - timedelta(days=7)
    unverified = User.objects.filter(
        is_verified=False,
        created_at__lt=week_ago
    )
    count = unverified.count()
    unverified.delete()
    logger.info(f"Cleaned up {count} unverified users")

@shared_task
def cleanup_expired_matches():
    now = timezone.now()
    expired = Match.objects.filter(expires_at__lt=now)
    count = expired.count()
    expired.delete()
    logger.info(f"Cleaned up {count} expired matches")

@shared_task
def cleanup_deleted_chats():
    thirty_days_ago = timezone.now() - timedelta(days=30)
    deleted = ChatRoom.objects.filter(
        is_deleted=True,
        deleted_at__lt=thirty_days_ago
    )
    count = deleted.count()
    deleted.delete()
    logger.info(f"Cleaned up {count} deleted chat rooms")

@shared_task
def verify_subscriptions():
    now = timezone.now()
    expired_subs = Subscription.objects.filter(
        status='success',
        expires_at__lt=now
    )
    
    for sub in expired_subs:
        sub.status = 'expired'
        sub.save(update_fields=['status'])
        
        chat = sub.chat_room
        if not chat.is_locked:
            chat.is_locked = True
            chat.locked_at = now
            chat.save(update_fields=['is_locked', 'locked_at'])
    
    logger.info(f"Verified {expired_subs.count()} subscriptions")

@shared_task
def cleanup_typing_indicators():
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    old_indicators = models.TypingIndicator.objects.filter(
        created_at__lt=five_minutes_ago
    )
    count = old_indicators.count()
    old_indicators.delete()
    logger.info(f"Cleaned up {count} stale typing indicators")

@shared_task
def retry_failed_emails(max_retries=3):
    from .models import AdminLog
    
    pending = AdminLog.objects.filter(
        action__in=['send_notification'],
        details__email_sent=False,
        details__retry_count__lt=max_retries
    )
    
    for log in pending:
        log.details['retry_count'] = log.details.get('retry_count', 0) + 1
        log.save(update_fields=['details'])
