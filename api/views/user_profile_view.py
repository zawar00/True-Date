from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from api.serializers import UserProfileSerializer
from api.services.user_profile_service import get_user_profile_by_id, create_user_profile, update_user_profile
from api.utils.logger import log_error, log_info
from rest_framework.exceptions import ValidationError

class UserProfileViewSet(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        try:
            # Fetch the user profile using the service layer
            profile = get_user_profile_by_id(pk)
            log_info(f"User profile retrieved for ID {pk}")
            
            # Serialize the retrieved profile
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            log_error(f"User profile not found for ID {pk}")
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            # Create a user profile using the service layer
            profile = create_user_profile(request.data)
            log_info(f"User profile created for user {profile.user.username}")
            
            # Serialize the created profile
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            log_error(f"Validation error during profile creation: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error(f"Error during profile creation: {e}")
            return Response({"error": "An error occurred while creating the profile."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        try:
            # Fetch and update the user profile using the service layer
            profile = update_user_profile(pk, request.data)
            log_info(f"User profile updated for ID {pk}")
            
            # Serialize the updated profile
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            log_error(f"User profile not found for ID {pk}")
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            log_error(f"Validation error during profile update: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error(f"Error during profile update: {e}")
            return Response({"error": "An error occurred while updating the profile."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
