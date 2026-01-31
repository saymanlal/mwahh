from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()
router.register(r'users', views.UserProfileViewSet, basename='user-profile')
router.register(r'matching', views.MatchingViewSet, basename='matching')
router.register(r'chat-rooms', views.ChatRoomViewSet, basename='chat-room')
router.register(r'stickers', views.StickerViewSet, basename='sticker')
router.register(r'gifts', views.GiftViewSet, basename='gift')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'admin', views.AdminViewSet, basename='admin')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/register/', views.register, name='register'),
    path('api/auth/verify-otp/', views.verify_otp, name='verify-otp'),
    path('api/auth/resend-otp/', views.resend_otp, name='resend-otp'),
    path('api/gifts/send/', views.send_gift, name='send-gift'),
    path('api/abuse/report/', views.report_abuse, name='report-abuse'),
]
