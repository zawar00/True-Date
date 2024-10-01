from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from api.models.user_profile import UserProfile, CustomUser
from api.serializers.user_profile_serializer import UserProfileSerializer
from api.utils.responses import success_response, error_response
# Custom permissions for role-based access
from api.permissions.permissions import IsAdminUser, IsRegularUser

# View to get all profiles of active users
class ActiveUserProfilesView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  # Require token

    def get(self, request):
        active_users = UserProfile.objects.filter(user__is_active=True)
        serializer = UserProfileSerializer(active_users, many=True)
        return success_response(data=serializer.data, message="Active user profiles retrieved successfully")


# View to get the logged-in user's profile
class UserProfileDetailView(APIView):
    permission_classes = [IsAuthenticated, IsRegularUser]  # Require token

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)  # Get the profile of the logged-in user
            serializer = UserProfileSerializer(profile)
            return success_response(data=serializer.data, message="Profile retrieved successfully")
        except UserProfile.DoesNotExist:
            return error_response(message="User profile not found", status_code=status.HTTP_404_NOT_FOUND)

# View to edit the logged-in user's profile
class UserProfileUpdateView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsRegularUser]  # Require token
    serializer_class = UserProfileSerializer

    def get_object(self):
        """Override to get the logged-in user's profile only"""
        return UserProfile.objects.get(user=self.request.user)

    def put(self, request, *args, **kwargs):
        """Handle full update requests"""
        response = self.update(request, *args, **kwargs)
        return success_response(data=response.data, message="Profile updated successfully")

    def patch(self, request, *args, **kwargs):
        """Handle partial update requests"""
        response = self.partial_update(request, *args, **kwargs)
        return success_response(data=response.data, message="Profile updated successfully")