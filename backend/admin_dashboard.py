from django.contrib import admin
from django.utils.html import format_html
from .api.models import (
    User, EmailVerification, InstitutionDomain, MatchProfile, Match,
    ChatRoom, ChatMessage, Sticker, Gift, Notification, Subscription,
    AbuseReport, AdminLog, PaymentReminder
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['anonymous_handle', 'email', 'is_verified', 'is_institutional', 'is_banned', 'tokens_balance', 'created_at']
    list_filter = ['is_verified', 'is_institutional', 'is_banned', 'created_at']
    search_fields = ['email', 'anonymous_handle']
    readonly_fields = ['user_uuid', 'anonymous_handle', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Identity', {'fields': ('user_uuid', 'email', 'anonymous_handle')}),
        ('Verification', {'fields': ('is_verified', 'is_institutional', 'verified_at')}),
        ('Status', {'fields': ('is_banned', 'banned_at', 'ban_reason')}),
        ('Profile', {'fields': ('gender', 'age', 'height_cm', 'degree', 'profession', 'city', 'state', 'bio', 'interests', 'photos')}),
        ('Tokens', {'fields': ('tokens_balance',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    actions = ['ban_user', 'unban_user']
    
    def ban_user(self, request, queryset):
        queryset.update(is_banned=True)
    ban_user.short_description = "Ban selected users"
    
    def unban_user(self, request, queryset):
        queryset.update(is_banned=False)
    unban_user.short_description = "Unban selected users"

@admin.register(InstitutionDomain)
class InstitutionDomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'institution_name', 'country', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'country']
    search_fields = ['domain', 'institution_name']
    readonly_fields = ['created_at']

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_a', 'user_b', 'is_locked', 'is_deleted', 'created_at', 'expires_at']
    list_filter = ['is_locked', 'is_deleted', 'created_at']
    search_fields = ['id', 'user_a__email', 'user_b__email']
    readonly_fields = ['id', 'created_at', 'last_activity']
    
    actions = ['lock_chat', 'unlock_chat', 'extend_chat']
    
    def lock_chat(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_locked=True, locked_at=timezone.now())
    lock_chat.short_description = "Lock selected chats"
    
    def unlock_chat(self, request, queryset):
        queryset.update(is_locked=False, locked_at=None)
    unlock_chat.short_description = "Unlock selected chats"
    
    def extend_chat(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        for room in queryset:
            room.expires_at = timezone.now() + timedelta(days=7)
            room.save()
    extend_chat.short_description = "Extend selected chats by 7 days"

@admin.register(Sticker)
class StickerAdmin(admin.ModelAdmin):
    list_display = ['name', 'tier', 'token_cost', 'is_active', 'category']
    list_filter = ['tier', 'is_active', 'category']
    search_fields = ['name']

@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ['name', 'token_cost', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'chat_room', 'status', 'amount_paise', 'expires_at']
    list_filter = ['status', 'started_at']
    search_fields = ['user__email', 'payment_id']
    readonly_fields = ['id', 'started_at']

@admin.register(AbuseReport)
class AbuseReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'reporter', 'reported_user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['reporter__email', 'reported_user__email']
    readonly_fields = ['created_at']
    
    actions = ['mark_resolved']
    
    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='resolved', resolved_at=timezone.now())
    mark_resolved.short_description = "Mark selected reports as resolved"

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'admin', 'action', 'target_user', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['admin__email', 'target_user__email']
    readonly_fields = ['id', 'created_at', 'details']

admin.site.site_header = 'Matchmaking Platform Admin'
admin.site.site_title = 'Admin Portal'
admin.site.index_title = 'Welcome to Admin Dashboard'
