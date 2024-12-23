from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from utils.response_helper import successResponse, errorResponse
from django.contrib.auth import authenticate
from user_api.users.models import User, UserProfile
from .serializers import (
    AdminRegisterSerializer,
    AdminLoginSerializer,
    ChangePasswordSerializer,
    AdminProfileEditSerializer,
    UserProfileSerializer
)
from rest_framework import status
from utils.permissions import IsAdminUser
from utils.pagination import paginate_and_serialize
from django.db.models import Q
from datetime import date


class AdminRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminRegisterSerializer(data=request.data)
        if serializer.is_valid():
            admin = serializer.save()
            return successResponse(data={"email": admin.email}, message="Admin registered successfully.", code=status.HTTP_201_CREATED)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            admin = authenticate(username=email, password=password)
            if admin and admin.is_verified and admin.user_role == 'admin':
                refresh = RefreshToken.for_user(admin)
                tokens = {
                    "refreshToken": str(refresh),
                    "token": str(refresh.access_token)
                }
                return successResponse(data=tokens, message="Login successful.")
            return errorResponse(message="Invalid credentials or unverified account.", code=status.HTTP_400_BAD_REQUEST)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)
    
class AdminGetProfileView(APIView):
    permission_classes = [IsAdminUser]  # Only authenticated admins can access their profile

    def get(self, request):
        try:
            admin_user = request.user  # The currently authenticated admin user

            # Ensure that the user has the 'admin' role
            if admin_user.user_role != 'admin':
                return errorResponse(message="You are not authorized to access admin profiles.", code=status.HTTP_403_FORBIDDEN)

            # Check if the user has a related profile
            if not hasattr(admin_user, 'profile'):
                # Optionally, create a profile here if you want to handle missing profiles automatically
                UserProfile.objects.create(user=admin_user, dob=date(1985, 5, 15), willing_to_drive='20')  # Create profile for the user if it doesn't exist
                admin_user.refresh_from_db()  # Refresh user to load the newly created profile
                return successResponse(message="Admin profile was created and retrieved successfully.")
            
            # Get the admin's profile
            profile = admin_user.profile  # Access the related profile
            serializer = UserProfileSerializer(profile)

            return successResponse(data=serializer.data, message="Admin profile retrieved successfully.")

        except Exception as e:
            # Log the exception or provide additional debugging information
            print(f"Error: {str(e)}")
            return errorResponse(message="An unexpected error occurred.", details=str(e), code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminChangePasswordView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save()
                return successResponse(message="Password changed successfully.")
            return errorResponse(message="Old password is incorrect.", code=status.HTTP_400_BAD_REQUEST)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

class AdminEditProfileView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request):
        profile = request.user.profile
        serializer = AdminProfileEditSerializer(instance=profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return successResponse(data=serializer.data, message="Profile updated successfully.")
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

class AdminGetAllUserProfilesView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            # Fetch query parameters
            page_size = int(request.query_params.get('page_size', 10))
            search_query = request.query_params.get('search', '').strip()

            # Base queryset
            profiles = UserProfile.objects.filter(user__user_role='user')

            # Apply search filters if provided
            if search_query:
                profiles = profiles.filter(
                    Q(user__username__icontains=search_query) | 
                    Q(user__email__icontains=search_query) |
                    Q(name__icontains=search_query)
                )

            # Order by user date joined (newest first)
            profiles = profiles.order_by('-user__date_joined')

            # Paginate queryset
            data = paginate_and_serialize(
                queryset=profiles,
                request=request,
                serializer_class=UserProfileSerializer,
                page_size=page_size
            )

            return successResponse(data=data, message="User profiles retrieved successfully.")
        except ValueError:
            return errorResponse(message="Invalid page_size or page value.", code=400)
        except Exception as e:
            return errorResponse(message=str(e), code=500)

class AdminGetUserProfileByIDView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        try:
            # Fetch the UserProfile where the user has user_role='user' and matches the user_id
            profile = UserProfile.objects.get(user__id=user_id, user__user_role='user')
            serializer = UserProfileSerializer(profile)
            return successResponse(data=serializer.data, message="User profile retrieved successfully.")
        except UserProfile.DoesNotExist:
            return errorResponse(message="User profile not found or not eligible for retrieval.", code=status.HTTP_404_NOT_FOUND)

class AdminApproveDisapproveUserProfileView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            # Fetch the User object with user_role='user' and the given ID
            user = User.objects.get(id=user_id, user_role='user')

            # Toggle the is_verified status
            user.is_verified = not user.is_verified
            user.save()

            # Return appropriate success message
            if user.is_verified:
                return successResponse(message="User profile is now verified.")
            else:
                return successResponse(message="User profile is now unverified.")
        except User.DoesNotExist:
            return errorResponse(message="User not found or not eligible for verification.", code=status.HTTP_404_NOT_FOUND)
