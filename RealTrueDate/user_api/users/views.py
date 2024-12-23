from rest_framework import status
from rest_framework.views import APIView
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, VerificationCode
from .serializers import (
    RegisterSerializer, OTPVerificationSerializer, LoginSerializer, 
    ChangePasswordSerializer, PasswordResetRequestSerializer, PasswordResetSerializer
)
from rest_framework.permissions import AllowAny
from utils.permissions import IsRegularUser
from utils.response_helper import successResponse, errorResponse  # Import the response helpers
import random
from datetime import timedelta
from utils.stripe_helper import get_user_active_subscription
from utils.helper import check_required_fields, get_remaining_swipes
from utils.email_helper import send_email

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            code = f"{random.randint(1000, 9999)}"
            expires_at = timezone.now() + timedelta(minutes=10)
            VerificationCode.objects.create(user=user, code=code, expires_at=expires_at)
            # Send OTP email
            email_context = {
                'name': (user.profile.name).title(),
                'otp_code': code,
                'action_type': 'Registration Verification',
                'otp_validity': 10,
                'current_year': timezone.now().year,
            }
            send_email(
                subject="Your Verification Code for Real True Date",
                template_name="templates/emails/otp_email.html",
                context=email_context,
                recipient_list=[user.email]  # Assuming `email` is a field on the user model
            )
            return successResponse(data = {}, message="Verification code sent.", code=status.HTTP_201_CREATED)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            try:
                user = User.objects.get(email=email)
                verification_code = VerificationCode.objects.get(user=user, code=code)
                if timezone.now() < verification_code.expires_at:
                    # user.is_verified = True
                    user.status = 'active'
                    user.save()
                    return successResponse(message="Verification successful.")
                return errorResponse(message="Code expired.", code=status.HTTP_400_BAD_REQUEST)
            except (User.DoesNotExist, VerificationCode.DoesNotExist):
                return errorResponse(message="Invalid code.", code=status.HTTP_400_BAD_REQUEST)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Extract the email from the request data
        email = request.data.get('email')
        if not email:
            return errorResponse(message="Email is required.", code=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if the user exists
            user = User.objects.get(email=email)
            print("user.profile", (user.profile.name).title())

            # If the user already has an OTP that has not expired, invalidate it
            VerificationCode.objects.filter(user=user, expires_at__gt=timezone.now()).delete()

            # Generate a new OTP
            code = f"{random.randint(1000, 9999)}"
            expires_at = timezone.now() + timedelta(minutes=10)  # OTP expiration time (10 minutes)

            # Create the new OTP and associate it with the user
            VerificationCode.objects.create(user=user, code=code, expires_at=expires_at)

            # Send the OTP email
            email_context = {
                'name': (user.profile.name).title(),
                'otp_code': code,
                'action_type': 'Resend Verification Code',
                'otp_validity': 10,
                'current_year': timezone.now().year,
            }
            send_email(
                subject="Your New OTP for Real True Date",
                template_name="templates/emails/resend_otp_email.html",  # HTML template for resending OTP
                context=email_context,
                recipient_list=[user.email]
            )

            # Return success response
            return successResponse(
                data = {},
                message="OTP resent successfully.",
                code=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return errorResponse(message="User not found.", code=status.HTTP_404_NOT_FOUND)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(username=email, password=password)
            if not user:
                return errorResponse(message="Invalid credentials.", code=status.HTTP_400_BAD_REQUEST)
            if user.status != 'active':
                return errorResponse(message="Account is not active.", code=status.HTTP_400_BAD_REQUEST)
            if not user.is_verified:
                return errorResponse(message="Account not verified.", code=status.HTTP_400_BAD_REQUEST)
        
            # Get active subscription using the helper function
            subscription_info = get_user_active_subscription(user)
            remaining_swipes = get_remaining_swipes(user)
            if user and user.user_role == 'user':
                refresh = RefreshToken.for_user(user)
                data = {
                    "refreshToken": str(refresh),
                    "token": str(refresh.access_token),
                    "is_verified": user.is_verified,
                    "status": user.status,
                    "subscription": subscription_info ,
                    "remaining_swipes": remaining_swipes
                }
                return successResponse(data=data, message="Login successful.")
            return errorResponse(message="Invalid credentials or unverified account.", code=status.HTTP_400_BAD_REQUEST)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsRegularUser] 

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

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                # Check if the user exists
                user = User.objects.get(email=email)
                print("user.profile", user.profile)

                # Invalidate any existing OTPs for password reset
                VerificationCode.objects.filter(user=user, expires_at__gt=timezone.now()).delete()

                # Generate a new OTP
                code = f"{random.randint(1000, 9999)}"
                expires_at = timezone.now() + timedelta(minutes=10)  # OTP valid for 10 minutes

                # Create and save the OTP
                VerificationCode.objects.create(user=user, code=code, expires_at=expires_at)

                # Send the OTP email for password reset
                email_context = {
                    'name': (user.profile.name).title(),
                    'otp_code': code,
                    'otp_validity': 10,
                    'current_year': timezone.now().year,
                }
                send_email(
                    subject="Password Reset Code for Real True Date",
                    template_name="templates/emails/forgot_password_otp_email.html",  # HTML template for password reset
                    context=email_context,
                    recipient_list=[user.email]
                )

                # Return success response
                return successResponse(
                    data = {},
                    message="Password reset OTP sent.",
                    code=status.HTTP_200_OK
                )

            except User.DoesNotExist:
                return errorResponse(
                    message="User not found.",
                    code=status.HTTP_404_NOT_FOUND
                )

        # Return validation error response
        return errorResponse(
            message="Validation failed.",
            details=serializer.errors,
            code=status.HTTP_400_BAD_REQUEST
        )

class PasswordResetView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']
            try:
                user = User.objects.get(email=email)
                verification_code = VerificationCode.objects.get(user=user, code=code)
                if timezone.now() < verification_code.expires_at:
                    user.set_password(new_password)
                    user.save()
                    return successResponse(message="Password reset successful.")
                return errorResponse(message="Code expired.", code=status.HTTP_400_BAD_REQUEST)
            except (User.DoesNotExist, VerificationCode.DoesNotExist):
                return errorResponse(message="Invalid code.", code=status.HTTP_400_BAD_REQUEST)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)