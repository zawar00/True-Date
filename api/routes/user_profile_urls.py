from django.urls import path
from api.views.user_profile_view import ActiveUserProfilesView, UserProfileDetailView, UserProfileUpdateView

urlpatterns = [
    path('profiles/', ActiveUserProfilesView.as_view(), name='active-user-profiles'),
    path('profile/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path('profiles/edit/', UserProfileUpdateView.as_view(), name='user-profile-update'),
]
