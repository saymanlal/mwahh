import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import secrets

class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('NB', 'Non-Binary'),
        ('O', 'Other'),
    ]
    
    user_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    anonymous_handle = models.CharField(max_length=32, unique=True)
    email = models.EmailField(unique=True)
    
    is_verified = models.BooleanField(default=False)
    is_institutional = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(18), MaxValueValidator(100)])
    height_cm = models.PositiveIntegerField(null=True, blank=True)
    
    degree = models.CharField(max_length=100, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='India')
    
    bio = models.TextField(blank=True, max_length=500)
    interests = models.JSONField(default=list, blank=True)
    photos = models.JSONField(default=list, blank=True)
    
    is_banned = models.BooleanField(default=False)
    banned_at = models.DateTimeField(null=True, blank=True)
    ban_reason = models.TextField(blank=True)
    
    tokens_balance = models.PositiveIntegerField(default=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_uuid']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['is_institutional']),
            models.Index(fields=['is_banned']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.anonymous_handle

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    otp_attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=5)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_verified']),
        ]
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_otp_locked(self):
        return self.otp_attempts >= self.max_attempts

class InstitutionDomain(models.Model):
    domain = models.CharField(max_length=255, unique=True)
    institution_name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_domains')
    
    class Meta:
        ordering = ['domain']
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"{self.domain} - {self.institution_name}"

class InstitutionEmailList(models.Model):
    institution_domain = models.ForeignKey(InstitutionDomain, on_delete=models.CASCADE, related_name='email_lists')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    emails = models.JSONField()
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']

class MatchProfile(models.Model):
    SCOPE_CHOICES = [
        ('same_institute', 'Same Institute'),
        ('city', 'City'),
        ('state', 'State'),
        ('national', 'National'),
        ('global', 'Global'),
    ]
    
    MODE_CHOICES = [
        ('friend', 'Friend'),
        ('hookup', 'Hookup'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='match_profile')
    preferred_mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='friend')
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='global')
    
    age_range_min = models.PositiveIntegerField(default=18, validators=[MinValueValidator(18)])
    age_range_max = models.PositiveIntegerField(default=60, validators=[MaxValueValidator(100)])
    
    height_range_min_cm = models.PositiveIntegerField(null=True, blank=True)
    height_range_max_cm = models.PositiveIntegerField(null=True, blank=True)
    
    preferred_interests = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['preferred_mode']),
        ]

class Match(models.Model):
    SCORE_ALGORITHM_VERSION = 1
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_a')
    user_b = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_b')
    
    mode = models.CharField(max_length=10, choices=[('friend', 'Friend'), ('hookup', 'Hookup')])
    match_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    chat_room = models.OneToOneField('ChatRoom', on_delete=models.SET_NULL, null=True, blank=True, related_name='match')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_a', 'user_b']),
            models.Index(fields=['created_at']),
            models.Index(fields=['chat_room']),
        ]
        unique_together = [('user_a', 'user_b')]
    
    def __str__(self):
        return f"Match: {self.user_a.anonymous_handle} <-> {self.user_b.anonymous_handle}"

class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_a')
    user_b = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_b')
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, blank=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['user_a', 'user_b']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_locked']),
        ]
        unique_together = [('user_a', 'user_b')]
    
    def __str__(self):
        return f"ChatRoom: {self.user_a.anonymous_handle} <-> {self.user_b.anonymous_handle}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def days_remaining(self):
        if self.is_expired():
            return 0
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)

class ChatMessage(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('voice', 'Voice'),
        ('sticker', 'Sticker'),
        ('gift', 'Gift'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES)
    content = models.TextField(blank=True)
    media_url = models.URLField(blank=True)
    
    is_seen = models.BooleanField(default=False)
    seen_at = models.DateTimeField(null=True, blank=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', 'created_at']),
            models.Index(fields=['sender']),
            models.Index(fields=['is_seen']),
        ]
    
    def __str__(self):
        return f"Message: {self.sender.anonymous_handle} in {self.room.id}"

class TypingIndicator(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='typing_indicators')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [('room', 'user')]
        indexes = [
            models.Index(fields=['room', 'created_at']),
        ]

class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='subscriptions')
    
    payment_id = models.CharField(max_length=255, unique=True)
    amount_paise = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default='INR')
    
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ])
    
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    payment_method = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'chat_room']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
        ]
    
    def is_active(self):
        return self.status == 'success' and timezone.now() < self.expires_at

class TokenTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('gift', 'Gift Purchase'),
        ('sticker', 'Premium Sticker'),
        ('refund', 'Refund'),
        ('bonus', 'Bonus'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_transactions')
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.IntegerField()
    balance_before = models.PositiveIntegerField()
    balance_after = models.PositiveIntegerField()
    
    description = models.TextField(blank=True)
    related_object_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

class Sticker(models.Model):
    TIER_CHOICES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='free')
    
    image_url = models.URLField()
    thumbnail_url = models.URLField()
    
    token_cost = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    category = models.CharField(max_length=50, blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_stickers')
    
    class Meta:
        ordering = ['tier', 'name']
        indexes = [
            models.Index(fields=['tier', 'is_active']),
            models.Index(fields=['category']),
        ]

class Gift(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    image_url = models.URLField()
    animation_url = models.URLField(blank=True)
    
    token_cost = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_gifts')
    
    class Meta:
        ordering = ['token_cost']
        indexes = [
            models.Index(fields=['is_active']),
        ]

class SentGift(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE, related_name='sent_gifts')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gifts_sent')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gifts_received')
    
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='sent_gifts')
    message = models.CharField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'recipient']),
            models.Index(fields=['chat_room']),
        ]

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('match', 'Match'),
        ('message', 'New Message'),
        ('payment_reminder', 'Payment Reminder'),
        ('chat_expiring', 'Chat Expiring'),
        ('admin_alert', 'Admin Alert'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    body = models.TextField()
    
    related_room_id = models.UUIDField(null=True, blank=True)
    related_object_id = models.CharField(max_length=255, blank=True)
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    is_dismissed = models.BooleanField(default=False)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
        ]

class PaymentReminder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='payment_reminders')
    
    reminder_type = models.CharField(max_length=50)
    media_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['scheduled_at', 'sent_at']),
        ]

class AbuseReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abuse_reports')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abuse_reports_against')
    
    reason = models.TextField()
    evidence_urls = models.JSONField(default=list, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_abuse_reports')
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['reported_user']),
        ]

class AdminLog(models.Model):
    ACTION_CHOICES = [
        ('user_ban', 'User Ban'),
        ('user_unban', 'User Unban'),
        ('delete_user', 'Delete User'),
        ('delete_chat', 'Delete Chat'),
        ('extend_chat', 'Extend Chat'),
        ('approve_domain', 'Approve Domain'),
        ('upload_sticker', 'Upload Sticker'),
        ('upload_gift', 'Upload Gift'),
        ('upload_reminder', 'Upload Reminder'),
        ('resolve_report', 'Resolve Report'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_logs')
    
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_actions_on')
    
    details = models.JSONField(default=dict)
    reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['admin', 'created_at']),
            models.Index(fields=['action']),
        ]
