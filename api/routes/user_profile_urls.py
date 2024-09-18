from django.urls import path
from api.views.user_profile_view import UserProfileViewSet

urlpatterns = [
    path('profiles/', UserProfileViewSet.as_view({'get': 'list', 'post': 'create'}), name='userprofile-list'),
    path('profiles/<int:pk>/', UserProfileViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='userprofile-detail'),
]
