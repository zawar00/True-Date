from django.urls import path
from .views import UserProfileView, UserProfileVideoView, BlockUserView, UnblockUserView, UserProfileByIdView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='profile'),  # Profile endpoint
    path('profileById/<int:pk>/', UserProfileByIdView.as_view(), name='user-profile-by-id'),
    path('profile/video/', UserProfileVideoView.as_view(), name='profile-video'),  # Profile endpoint
    path('block-user/', BlockUserView.as_view(), name='block_user'),
    path('unblock-user/', UnblockUserView.as_view(), name='unblock_user'),
]
