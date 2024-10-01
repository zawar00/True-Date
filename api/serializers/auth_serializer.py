from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from api.models.user_profile import CustomUser, UserOTP, UserProfile
import random
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['dob', 'gender', 'interested_in', 'willing_to_drive', 'bio', 'location']

class RegistrationSerializer(serializers.ModelSerializer):
    profile_data = UserProfileSerializer(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'password', 'time_zone', 'device_id', 'profile_data']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile_data', None)
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            time_zone=validated_data.get('time_zone', None),
            device_id=validated_data.get('device_id', None),
        )
        
        if profile_data:
            UserProfile.objects.create(user=user, **profile_data)
        
        # Generate and save OTP
        self.generate_and_send_otp(user)

        return user

    def generate_and_send_otp(self, user):
        otp_code = str(random.randint(100000, 999999))
        otp_expiry = timezone.now() + timedelta(minutes=10)
        UserOTP.objects.create(user=user, otp_code=otp_code, expires_at=otp_expiry)
        print(f"OTP sent to {user.email}: {otp_code}")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        profile = instance.userprofile if hasattr(instance, 'userprofile') else None
        representation['profile'] = UserProfileSerializer(profile).data if profile else None
        return representation

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data['email'])
            otp_entry = UserOTP.objects.filter(user=user, otp_code=data['otp_code'], verified=False).order_by('-created_at').first()
            if otp_entry is None:
                raise serializers.ValidationError("Invalid OTP")
            if otp_entry.expires_at < timezone.now():
                raise serializers.ValidationError("OTP expired")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found")
        
        return data

    def save(self, **kwargs):
        user = CustomUser.objects.get(email=self.validated_data['email'])
        otp_entry = UserOTP.objects.filter(user=user, otp_code=self.validated_data['otp_code'], verified=False).order_by('-created_at').first()
        otp_entry.verified = True
        otp_entry.save()
        user.is_verified = True
        user.save()
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data['email'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found")
        return data

    def save(self, **kwargs):
        user = CustomUser.objects.get(email=self.validated_data['email'])
        self.generate_and_send_otp(user)

    def generate_and_send_otp(self, user):
        otp_code = str(random.randint(100000, 999999))
        otp_expiry = timezone.now() + timedelta(minutes=10)
        UserOTP.objects.create(user=user, otp_code=otp_code, expires_at=otp_expiry)
        print(f"OTP sent to {user.email}: {otp_code}")

class PasswordResetVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data['email'])
            otp_entry = UserOTP.objects.filter(user=user, otp_code=data['otp_code'], verified=False).order_by('-created_at').first()
            if otp_entry is None:
                raise serializers.ValidationError("Invalid OTP")
            if otp_entry.expires_at < timezone.now():
                raise serializers.ValidationError("OTP expired")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found")
        
        return data

    def save(self, **kwargs):
        user = CustomUser.objects.get(email=self.validated_data['email'])
        otp_entry = UserOTP.objects.filter(user=user, otp_code=self.validated_data['otp_code']).order_by('-created_at').first()
        otp_entry.verified = True
        otp_entry.save()
        return user

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data['email'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found")
        return data

    def save(self, **kwargs):
        user = CustomUser.objects.get(email=self.validated_data['email'])
        user.set_password(self.validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data['email']
        password = data['password']

        # Attempt to get the user by email
        user = CustomUser.objects.filter(email=email).first()
        if user is None:
            raise serializers.ValidationError("User not found")

        # Validate the password
        if not user.check_password(password):  # Use check_password method
            raise serializers.ValidationError("Invalid credentials")
        
        # Check if the user is verified
        if not user.is_verified:
            raise serializers.ValidationError("User is not verified. Please verify OTP.")

        # Return the user instance as part of validated data
        data['user'] = user
        return data

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        if len(value) < 8:  # Example: enforce a minimum length
            raise serializers.ValidationError("New password must be at least 8 characters long.")
        return value

    def save(self):
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return user
