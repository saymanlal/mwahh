from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from .models import (
    User, EmailVerification, InstitutionDomain, MatchProfile, Match, ChatRoom,
    ChatMessage, Notification, Sticker, Gift, SentGift, Subscription, TokenTransaction,
    AbuseReport, PaymentReminder
)
import secrets
import string

class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    gender = serializers.ChoiceField(choices=User.GENDER_CHOICES, required=False)
    age = serializers.IntegerField(required=False, min_value=18, max_value=100)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value.lower()
    
    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        
        handle = self._generate_anonymous_handle()
        user = User.objects.create_user(
            email=email,
            username=email,
            password=password,
            anonymous_handle=handle,
            gender=validated_data.get('gender', ''),
            age=validated_data.get('age'),
        )
        
        otp = self._generate_otp()
        expires_at = timezone.now() + timedelta(minutes=10)
        
        EmailVerification.objects.create(
            user=user,
            email=email,
            otp=otp,
            expires_at=expires_at,
        )
        
        return user, otp
    
    @staticmethod
    def _generate_anonymous_handle():
        while True:
            adjectives = ['swift', 'bold', 'calm', 'eager', 'free', 'gentle', 'happy', 'keen', 'lively', 'noble']
            animals = ['tiger', 'eagle', 'wolf', 'puma', 'lynx', 'otter', 'raven', 'hawk', 'fox', 'bear']
            numbers = str(secrets.randbelow(9999))
            handle = f"{secrets.choice(adjectives)}_{secrets.choice(animals)}{numbers}"
            
            if not User.objects.filter(anonymous_handle=handle).exists():
                return handle
    
    @staticmethod
    def _generate_otp():
        return ''.join(secrets.choice(string.digits) for _ in range(6))

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    
    def validate(self, data):
        email = data['email'].lower()
        otp = data['otp']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or OTP")
        
        try:
            verification = EmailVerification.objects.get(user=user, email=email)
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError("No verification request found")
        
        if verification.is_expired():
            raise serializers.ValidationError("OTP has expired")
        
        if verification.is_otp_locked():
            raise serializers.ValidationError("Too many attempts. Please request a new OTP")
        
        if verification.otp != otp:
            verification.otp_attempts += 1
            verification.save(update_fields=['otp_attempts'])
            raise serializers.ValidationError("Invalid OTP")
        
        data['user'] = user
        data['verification'] = verification
        return data

class InstitutionDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionDomain
        fields = ['id', 'domain', 'institution_name', 'country', 'is_approved']

class UserProfileSerializer(serializers.ModelSerializer):
    match_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'user_uuid', 'anonymous_handle', 'gender', 'age', 'height_cm',
            'degree', 'profession', 'city', 'state', 'bio', 'interests',
            'photos', 'tokens_balance', 'is_verified', 'created_at', 'match_profile'
        ]
        read_only_fields = ['user_uuid', 'anonymous_handle', 'tokens_balance', 'is_verified']
    
    def get_match_profile(self, obj):
        try:
            return MatchProfileSerializer(obj.match_profile).data
        except:
            return None

class MatchProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchProfile
        fields = [
            'id', 'preferred_mode', 'scope', 'age_range_min', 'age_range_max',
            'height_range_min_cm', 'height_range_max_cm', 'preferred_interests', 'is_active'
        ]

class MatchSerializer(serializers.ModelSerializer):
    user_a_handle = serializers.CharField(source='user_a.anonymous_handle', read_only=True)
    user_b_handle = serializers.CharField(source='user_b.anonymous_handle', read_only=True)
    
    class Meta:
        model = Match
        fields = ['id', 'user_a_handle', 'user_b_handle', 'mode', 'created_at', 'expires_at']

class ChatRoomSerializer(serializers.ModelSerializer):
    user_a_handle = serializers.CharField(source='user_a.anonymous_handle', read_only=True)
    user_b_handle = serializers.CharField(source='user_b.anonymous_handle', read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'user_a_handle', 'user_b_handle', 'created_at', 'expires_at',
            'is_locked', 'days_remaining', 'last_activity'
        ]
        read_only_fields = ['id', 'created_at', 'expires_at', 'is_locked']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_handle = serializers.CharField(source='sender.anonymous_handle', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'sender_handle', 'message_type', 'content', 'media_url',
            'is_seen', 'is_deleted', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'sender_handle']

class StickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sticker
        fields = [
            'id', 'name', 'description', 'tier', 'image_url', 'thumbnail_url',
            'token_cost', 'category', 'tags', 'is_active'
        ]

class GiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gift
        fields = [
            'id', 'name', 'description', 'image_url', 'animation_url',
            'token_cost', 'is_active'
        ]

class SentGiftSerializer(serializers.ModelSerializer):
    gift_details = GiftSerializer(source='gift', read_only=True)
    sender_handle = serializers.CharField(source='sender.anonymous_handle', read_only=True)
    
    class Meta:
        model = SentGift
        fields = [
            'id', 'gift_details', 'sender_handle', 'message', 'created_at'
        ]

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            'id', 'payment_id', 'amount_paise', 'currency', 'status',
            'started_at', 'expires_at'
        ]
        read_only_fields = ['id', 'started_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'body', 'related_room_id',
            'is_read', 'is_dismissed', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class PaymentReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentReminder
        fields = ['id', 'reminder_type', 'media_url', 'scheduled_at', 'sent_at']

class AbuseReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbuseReport
        fields = [
            'id', 'reported_user', 'reason', 'evidence_urls',
            'status', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']

class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_uuid', 'email', 'anonymous_handle', 'age', 'is_verified',
            'is_institutional', 'is_banned', 'created_at', 'tokens_balance'
        ]
        read_only_fields = fields

class TokenTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenTransaction
        fields = [
            'id', 'transaction_type', 'amount', 'balance_before', 'balance_after',
            'description', 'created_at'
        ]
        read_only_fields = fields
