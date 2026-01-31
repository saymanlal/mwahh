from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'api'

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('auth/verify-otp/', views.verify_otp, name='verify_otp'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UpdateProfileView.as_view(), name='update_profile'),
    
    path('matches/', views.MatchListView.as_view(), name='matches'),
    path('matches/<uuid:match_uuid>/', views.MatchDetailView.as_view(), name='match_detail'),
    path('matches/<uuid:match_uuid>/accept/', views.AcceptMatchView.as_view(), name='accept_match'),
    path('matches/<uuid:match_uuid>/reject/', views.RejectMatchView.as_view(), name='reject_match'),
    
    path('chats/', views.ChatRoomListView.as_view(), name='chats'),
    path('chats/<uuid:room_uuid>/', views.ChatRoomDetailView.as_view(), name='chat_detail'),
    path('chats/<uuid:room_uuid>/messages/', views.ChatMessageListView.as_view(), name='chat_messages'),
    path('chats/<uuid:room_uuid>/mark-seen/', views.MarkMessagesSeenView.as_view(), name='mark_seen'),
    
    path('stickers/', views.StickerListView.as_view(), name='stickers'),
    path('gifts/', views.GiftListView.as_view(), name='gifts'),
    path('gifts/<uuid:gift_uuid>/send/', views.SendGiftView.as_view(), name='send_gift'),
    
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<uuid:notification_uuid>/dismiss/', views.DismissNotificationView.as_view(), name='dismiss_notification'),
    
    path('tokens/purchase/', views.PurchaseTokensView.as_view(), name='purchase_tokens'),
    path('tokens/history/', views.TokenHistoryView.as_view(), name='token_history'),
    
    path('subscriptions/', views.SubscriptionListView.as_view(), name='subscriptions'),
    path('subscriptions/<uuid:subscription_uuid>/subscribe/', views.CreateSubscriptionView.as_view(), name='create_subscription'),
    
    path('blocks/', views.BlockListView.as_view(), name='blocks'),
    path('blocks/<uuid:user_uuid>/', views.BlockUserView.as_view(), name='block_user'),
    
    path('reports/', views.AbuseReportListView.as_view(), name='reports'),
    path('reports/<uuid:user_uuid>/', views.CreateAbuseReportView.as_view(), name='create_report'),
    
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_users'),
    path('admin/users/<uuid:user_uuid>/ban/', views.AdminBanUserView.as_view(), name='admin_ban_user'),
    path('admin/users/<uuid:user_uuid>/delete/', views.AdminDeleteUserView.as_view(), name='admin_delete_user'),
    path('admin/chats/', views.AdminChatListView.as_view(), name='admin_chats'),
    path('admin/chats/<uuid:room_uuid>/lock/', views.AdminLockChatView.as_view(), name='admin_lock_chat'),
    path('admin/chats/<uuid:room_uuid>/unlock/', views.AdminUnlockChatView.as_view(), name='admin_unlock_chat'),
    path('admin/chats/<uuid:room_uuid>/extend/', views.AdminExtendChatView.as_view(), name='admin_extend_chat'),
    path('admin/chats/<uuid:room_uuid>/delete/', views.AdminDeleteChatView.as_view(), name='admin_delete_chat'),
    path('admin/domains/', views.AdminDomainListView.as_view(), name='admin_domains'),
    path('admin/domains/<int:domain_id>/approve/', views.AdminApproveDomainView.as_view(), name='admin_approve_domain'),
    path('admin/payments/', views.AdminPaymentListView.as_view(), name='admin_payments'),
    path('admin/reports/', views.AdminReportListView.as_view(), name='admin_reports'),
    path('admin/reports/<uuid:report_uuid>/resolve/', views.AdminResolveReportView.as_view(), name='admin_resolve_report'),
]
