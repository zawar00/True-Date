from rest_framework import serializers
from user_api.users.models import User, UserProfile

class AdminRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_role']

    def create(self, validated_data):
        validated_data['user_role'] = 'admin'  # Ensure the role is set to admin
        admin = User.objects.create_user(**validated_data)
        return admin


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for nested User data within the profile."""
    class Meta:
        model = User
        fields = ['id', 'email', 'is_verified', 'time_zone', 'user_role','is_active']  # Add any other user fields you want to include
        read_only_fields = ['id', 'is_verified', 'user_role', 'is_active']


class AdminProfileEditSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Allow updating nested user data
    
    class Meta:
        model = UserProfile
        fields = ['user', 'name', 'phone', 'dob', 'gender', 'interested_in', 'location', 'willing_to_drive', 'is_active', 'images', 'videos']
        read_only_fields = ['is_active']

    def update(self, instance, validated_data):
        # Extract nested user data and profile data
        user_data = validated_data.pop('user', None)
        
        # Update UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update User fields if provided
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ['user', 'name', 'phone', 'dob', 'gender', 'interested_in', 'location', 'is_active', 'willing_to_drive', 'images', 'videos']
