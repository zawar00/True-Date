from django.urls import path
from .views import (
    AdminRegisterView,
    AdminLoginView,
    AdminGetProfileView,
    AdminChangePasswordView,
    AdminEditProfileView,
    AdminGetAllUserProfilesView,
    AdminGetUserProfileByIDView,
    AdminApproveDisapproveUserProfileView
)

urlpatterns = [
    path('register/', AdminRegisterView.as_view(), name='admin-register'),
    path('login/', AdminLoginView.as_view(), name='admin-login'),
    path('change-password/', AdminChangePasswordView.as_view(), name='admin-change-password'),
    path('profile/', AdminGetProfileView.as_view(), name='admin-get-profile'),
    path('edit-profile/', AdminEditProfileView.as_view(), name='admin-edit-profile'),
    path('users/', AdminGetAllUserProfilesView.as_view(), name='admin-get-all-users'),
    path('users/<int:user_id>/', AdminGetUserProfileByIDView.as_view(), name='admin-get-user-profile'),
    path('users/profile-verification/<int:user_id>/', AdminApproveDisapproveUserProfileView.as_view(), name='admin-profile-verification-user'),
]