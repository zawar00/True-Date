import uuid
from rest_framework import serializers
from .models import User, UserProfile

class RegisterSerializer(serializers.ModelSerializer):
    profile_data = serializers.JSONField()
    images = serializers.ListField(
        child=serializers.CharField(max_length=255), required=False, default=list
    )
    videos = serializers.ListField(
        child=serializers.CharField(max_length=255), required=False, default=list
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'time_zone', 'profile_data', 'images', 'videos']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile_data')
        images = validated_data.pop('images', [])
        videos = validated_data.pop('videos', [])
        password = validated_data.pop('password')
        username = validated_data.get('email') or str(uuid.uuid4())
        
        user = User.objects.create(username=username, **validated_data)
        user.set_password(password)
        user.save()

        UserProfile.objects.create(
            user=user,
            name=profile_data.get('name'),
            phone=profile_data.get('phone'),
            dob=profile_data.get('dob'),
            gender=profile_data.get('gender'),
            interested_in=profile_data.get('interested_in'),
            location=profile_data.get('location'),
            willing_to_drive=profile_data.get('willing_to_drive'),
            images=images,
            videos=videos,
        )
        return user

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
