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

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            code = f"{random.randint(100000, 999999)}"
            expires_at = timezone.now() + timedelta(minutes=10)
            VerificationCode.objects.create(user=user, code=code, expires_at=expires_at)
            return successResponse({"code": code}, message="Verification code sent.", code=status.HTTP_201_CREATED)
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
                    user.is_verified = True
                    user.save()
                    return successResponse(message="Verification successful.")
                return errorResponse(message="Code expired.", code=status.HTTP_400_BAD_REQUEST)
            except (User.DoesNotExist, VerificationCode.DoesNotExist):
                return errorResponse(message="Invalid code.", code=status.HTTP_400_BAD_REQUEST)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(username=email, password=password)
            if user and user.is_verified and user.user_role == 'user':
                refresh = RefreshToken.for_user(user)
                tokens = {
                    "refreshToken": str(refresh),
                    "token": str(refresh.access_token)
                }
                return successResponse(data=tokens, message="Login successful.")
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
                user = User.objects.get(email=email)
                code = f"{random.randint(100000, 999999)}"
                expires_at = timezone.now() + timedelta(minutes=10)
                VerificationCode.objects.create(user=user, code=code, expires_at=expires_at)
                return successResponse({"code": code}, message="Password reset code sent.")
            except User.DoesNotExist:
                return errorResponse(message="User not found.", code=status.HTTP_404_NOT_FOUND)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

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
