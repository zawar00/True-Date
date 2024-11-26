from rest_framework import serializers
from user_api.users.models import UserProfile, User  # Import User model
from utils.uploadFiles import get_presigned_url

class UserSerializer(serializers.ModelSerializer):
    """Serializer for nested User data within the profile."""
    class Meta:
        model = User
        fields = ['id', 'email', 'is_verified', 'time_zone']  # Add any other user fields
        read_only_fields = ['id', 'is_verified']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested user data
    images = serializers.ListField(child=serializers.CharField(), required=False)
    videos = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = UserProfile
        fields = ['user', 'name', 'phone', 'dob', 'gender', 'interested_in', 'location', 'willing_to_drive', 'is_active', 'images', 'videos']
        read_only_fields = ['is_active']
        
    def to_representation(self, instance):
        """Override to dynamically generate pre-signed URLs for output."""
        representation = super().to_representation(instance)

        # Safely handle None values for images and videos
        representation['images'] = [
            get_presigned_url(image_key) for image_key in (instance.images or [])
        ]
        representation['videos'] = [
            get_presigned_url(video_key) for video_key in (instance.videos or [])
        ]

        return representation

    def update(self, instance, validated_data):
        # Handle nested user data updates
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # Handle images and videos updates if provided
        if 'images' in validated_data:  # Check if the key exists
            instance.images = validated_data['images']

        if 'videos' in validated_data:  # Check if the key exists
            instance.videos = validated_data['videos']

        # Update remaining UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
