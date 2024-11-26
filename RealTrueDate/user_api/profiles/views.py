from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from user_api.users.models import UserProfile
from .serializers import UserProfileSerializer
from utils.permissions import IsRegularUser  # Import the permission for regular users
from utils.response_helper import successResponse, errorResponse  # Import the response helpers

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated, IsRegularUser]  # Requires user to be logged in and a regular user

    def get(self, request):
        """Retrieve the user's profile if it is active."""
        try:
            profile = request.user.profile  # Access the user's profile
            if not profile.is_active:
                return errorResponse(message="Profile not found.", code=status.HTTP_404_NOT_FOUND)
            serializer = UserProfileSerializer(profile)
            return successResponse(data=serializer.data, message="Profile retrieved successfully.", code=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return errorResponse(message="Profile not found.", code=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Create a profile for the logged-in user if it doesn't already exist."""
        if hasattr(request.user, 'profile'):
            return errorResponse(message="Profile already exists.", code=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile = UserProfile.objects.create(user=request.user, **serializer.validated_data)
            return successResponse(data=UserProfileSerializer(profile).data, message="Profile created successfully.", code=status.HTTP_201_CREATED)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Update the user's profile if it is active."""
        try:
            # print("data:::::::::",request.data)
            profile = request.user.profile
            if not profile.is_active:
                return errorResponse(message="Profile not found.", code=status.HTTP_404_NOT_FOUND)
            
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return successResponse(data=serializer.data, message="Profile updated successfully.", code=status.HTTP_200_OK)
            return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return errorResponse(message="Profile not found.", code=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        """Soft delete the user's profile by setting is_active to False."""
        try:
            profile = request.user.profile
            profile.is_active = False
            profile.save()
            return successResponse(message="Profile deleted successfully.", code=status.HTTP_204_NO_CONTENT)
        except UserProfile.DoesNotExist:
            return errorResponse(message="Profile not found.", code=status.HTTP_404_NOT_FOUND)
