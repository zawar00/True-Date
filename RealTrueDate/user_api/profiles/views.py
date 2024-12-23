from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from user_api.users.models import User, UserProfile
from .models import Block
from .serializers import UserProfileSerializer, UserProfileVideoSerializer, BlockUserSerializer, BlockedUserSerializer, UserWithBlockStatusSerializer
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
        
class UserProfileVideoView(APIView):
    permission_classes = [IsAuthenticated, IsRegularUser]  # Requires user to be logged in and a regular user

    def get(self, request):
        """Retrieve the user's profile video if it is active."""
        try:
            profile = request.user.profile
            if not profile.is_active:
                return errorResponse(message="Profile not found.", code=status.HTTP_404_NOT_FOUND)
            serializer = UserProfileVideoSerializer(profile)
            return successResponse(data=serializer.data, message="Profile retrieved successfully.", code=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return errorResponse(message="Profile not found.", code=status.HTTP_404_NOT_FOUND)
        
# Block a user
class BlockUserView(APIView):
    permission_classes = [IsRegularUser]

    def post(self, request):
        serializer = BlockUserSerializer(data=request.data)
        if serializer.is_valid():
            blocked_user_id = serializer.validated_data['blocked_user_id']
            reason = serializer.validated_data.get('reason', '')  # Default to empty string if not provided
            try:
                blocked_user = User.objects.get(id=blocked_user_id)
                # Create or update the Block relationship with a reason
                block, created = Block.objects.get_or_create(
                    blocker=request.user, blocked=blocked_user
                )
                
                block.reason = reason  # Update reason if block already exists
                block.save()

                return successResponse(message=f"You have blocked {blocked_user.email} with reason: {reason or 'no reason'}.")
            except User.DoesNotExist:
                return errorResponse(message="User not found.", code=status.HTTP_404_NOT_FOUND)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        # Get all users blocked by the current user
        blocked_relations = Block.objects.filter(blocker=request.user)
        blocked_users = [relation.blocked for relation in blocked_relations]

        # Serialize the blocked users
        serializer = BlockedUserSerializer(blocked_users, many=True, context={'request': request})
        return successResponse(data={"blocked_users": serializer.data}, code=200)

# Unblock a user
class UnblockUserView(APIView):
    permission_classes = [IsRegularUser]

    def post(self, request):
        serializer = BlockUserSerializer(data=request.data)
        if serializer.is_valid():
            blocked_user_id = serializer.validated_data['blocked_user_id']
            try:
                blocked_user = User.objects.get(id=blocked_user_id)
                block_relation = Block.objects.filter(blocker=request.user, blocked=blocked_user)
                if block_relation.exists():
                    block_relation.delete()
                    return successResponse(message=f"You have unblocked {blocked_user.email}.")
                return errorResponse(message="User is not blocked.", code=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return errorResponse(message="User not found.", code=status.HTTP_404_NOT_FOUND)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)
    
class UserProfileByIdView(APIView):
    permission_classes = [IsAuthenticated, IsRegularUser]  # Requires user to be logged in and a regular user

    def get(self, request, pk):
        """Retrieve the profile of a user by ID with block status."""
        try:
            # Fetch the requested user's profile by the primary key (ID)
            user = User.objects.get(id=pk)
            profile = user.profile  # Access the profile via the user relationship
            
            if not profile.is_active:
                return errorResponse(message="Profile not found.", code=status.HTTP_404_NOT_FOUND)
            
            # Serialize user data with block status
            serializer = UserWithBlockStatusSerializer(user, context={'request': request})
            return successResponse(data=serializer.data, message="Profile retrieved successfully.", code=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return errorResponse(message="User not found.", code=status.HTTP_404_NOT_FOUND)
        
        except UserProfile.DoesNotExist:
            return errorResponse(message="Profile not found.", code=status.HTTP_404_NOT_FOUND)
