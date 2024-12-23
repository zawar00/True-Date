from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from user_api.users.models import UserProfile, User
from utils.response_helper import successResponse, errorResponse
from utils.uploadFiles import get_presigned_url
from utils.helper import calculate_age, get_filtered_users
from utils.permissions import IsRegularUser
from .models import Swipe
from .serializers import SwipeSerializer
from utils.helper import get_remaining_swipes

class MatchListView(APIView):
    permission_classes = [IsRegularUser]

    def get(self, request, format=None):
        """Retrieve potential matches for the logged-in user based on preferences."""
        try:
            user = request.user
            user_profile = user.profile

            if not user.is_verified:
                return errorResponse(message="Your account is either inactive or not verified.", code=status.HTTP_400_BAD_REQUEST)

            if not user_profile.is_active:
                return errorResponse(message="Your profile is not active.", code=status.HTTP_400_BAD_REQUEST)
            
            # Check remaining swipes
            # if get_remaining_swipes(user) <= 0:  # Check if the user has swipes left
            #     return errorResponse(message="You have no remaining swipes. Please upgrade your plan.", code=status.HTTP_400_BAD_REQUEST)

            user_age = calculate_age(user_profile.dob)

            age_min = user_profile.age_min or 18
            age_max = user_profile.age_max or user_age + 5

            if user_profile.location_point is None:
                return errorResponse(message="User location is not set.", code=status.HTTP_400_BAD_REQUEST)

            user_location = Point(user_profile.location_point.x, user_profile.location_point.y, srid=4326)

            excluded_user_ids = get_filtered_users(request)
            
            matches = UserProfile.objects.filter(
                is_active=True,
                user__is_verified=True,
                user__user_role='user',
            ).filter(
                age_min__gte=age_min,
                age_max__lte=age_max,
            ).annotate(
                distance=Distance('location_point', user_location)
            ).filter(
                # willing_to_drive__lte=user_profile.willing_to_drive * 1000,
            ).filter(
                gender=user_profile.interested_in,
            ).exclude(
                distance__isnull=True
            ).order_by('distance')

            # matches = UserProfile.objects.filter(
            #     is_active=True,
            #     user__is_verified=True,
            #     user__user_role='user',
            # ).filter(
            #     age_min__gte=age_min,
            #     age_max__lte=age_max,
            # ).annotate(
            #     distance=Distance('location_point', user_location)
            # ).filter(
            #     # willing_to_drive__lte=user_profile.willing_to_drive * 1000,
            # ).filter(
            #     gender=user_profile.interested_in,
            # ).exclude(
            #     user__id__in=excluded_user_ids  # Exclude blocked users
            # ).exclude(
            #     distance__isnull=True
            # ).order_by('distance')

            # matches = UserProfile.objects.filter(
            #     is_active=True,
            #     user__is_verified=True,
            #     user__user_role='user',
            # ).filter(
            #     age_min__lte=age_min,
            #     age_max__gte=age_max,
            # ).annotate(
            #     distance=Distance('location_point', user_location)
            # ).filter(
            #     willing_to_drive__lte=user_profile.willing_to_drive * 1000,
            # ).filter(
            #     gender=user_profile.interested_in,
            # ).exclude(
            #     distance__isnull=True
            # ).order_by('distance')

            match_data = []
            for match in matches:
                distance_km = match.distance.m / 1000 if match.distance is not None else 0

                user_age = calculate_age(match.dob)
                match_info = {
                    'user_id': match.user.id,
                    'name': match.name,
                    'age': user_age,
                    'distance': distance_km,
                    'gender': match.gender,
                    'location': match.location,
                    'interested_in': match.interested_in,
                    'images': [
                        get_presigned_url(image_key) for image_key in (match.images or [])
                    ]
                }
                match_data.append(match_info)

            return successResponse(data=match_data, message="Matches retrieved successfully.", code=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return errorResponse(message="User profile not found.", code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(str(e))
            return errorResponse(message=str(e), code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SwipeViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            target_user_id = request.data.get('target_user')
            direction = request.data.get('direction')

            if direction not in ['left', 'right']:
                return errorResponse(message="Invalid swipe direction", code=status.HTTP_400_BAD_REQUEST)

            if user.id == target_user_id:
                return errorResponse(message="You cannot swipe on yourself", code=status.HTTP_400_BAD_REQUEST)

            if Swipe.objects.filter(user=user, target_user_id=target_user_id).exists():
                return errorResponse(message="You have already swiped on this user", code=status.HTTP_400_BAD_REQUEST)

            try:
                target_user = User.objects.get(id=target_user_id)
            except User.DoesNotExist:
                return errorResponse(message="Target user not found", code=status.HTTP_404_NOT_FOUND)

            if target_user.user_role != 'user':
                return errorResponse(message="Users must have the 'user' role to swipe", code=status.HTTP_400_BAD_REQUEST)
            
            if not target_user.is_active:
                return errorResponse(message="Users must be active to swipe", code=status.HTTP_400_BAD_REQUEST)

            swipe = Swipe.objects.create(
                user=user,
                target_user=target_user,
                direction=direction
            )

            swipe_data = SwipeSerializer(swipe).data
            return successResponse(data=swipe_data, message="Swipe recorded successfully.", code=status.HTTP_201_CREATED)

        except Exception as e:
            return errorResponse(message=str(e), code=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
    def get(self, request, *args, **kwargs):
        try:
            # Get the authenticated user
            user = request.user

            # Get all the swipes where the direction is 'right' and the user is the authenticated user
            swipes = Swipe.objects.filter(user=user, direction='right')

            # If no right swipes are found, return a message indicating so
            if not swipes.exists():
                return errorResponse(message="No swipes found", code=status.HTTP_404_NOT_FOUND)

            # Serialize the swipe data
            swipe_data = SwipeSerializer(swipes, many=True).data

            # Return success response with serialized data
            return successResponse(data=swipe_data, message="Swipes retrieved successfully.", code=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception if necessary
            print(str(e))
            return errorResponse(message=str(e), code=status.HTTP_500_INTERNAL_SERVER_ERROR)