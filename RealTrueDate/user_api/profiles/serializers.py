from rest_framework import serializers
from user_api.users.models import UserProfile, User  # Import User model
from .models import Block
from utils.uploadFiles import get_presigned_url

class UserSerializer(serializers.ModelSerializer):
    """Serializer for nested User data within the profile."""
    class Meta:
        model = User
        fields = ['id', 'email', 'is_verified', 'status', 'time_zone']  # Add any other user fields
        read_only_fields = ['id', 'is_verified', 'status']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested user data
    images = serializers.ListField(child=serializers.CharField(), required=False)
    videos = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = UserProfile
        fields = ['user', 'name', 'phone', 'age_min', 'age_max', 'dob', 'gender', 'interested_in', 'zip_code', 'location', 'location_point', 'is_active', 'images', 'videos']
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

class UserProfileVideoSerializer(serializers.ModelSerializer):
    videos = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = UserProfile
        fields = [ 'videos']
        
    def to_representation(self, instance):
        """Override to dynamically generate pre-signed URLs for output."""
        representation = super().to_representation(instance)

        # Safely handle None values for images and videos
        representation['videos'] = [
            get_presigned_url(video_key) for video_key in (instance.videos or [])
        ]

        return representation
    
# Serializer to block/unblock a user
class BlockUserSerializer(serializers.Serializer):
    blocked_user_id = serializers.IntegerField()
    reason = serializers.CharField(required=False, allow_blank=True)  # Optional field

    def validate_blocked_user_id(self, value):
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        return value

# Serializer to retrieve blocked users
class BlockedUserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='id')  # Map the `id` field of User to `user_id`
    block_id = serializers.SerializerMethodField()  # Custom method to get Block model's ID
    reason = serializers.SerializerMethodField()  # Custom method to get reason
    name = serializers.CharField(source='profile.name', read_only=True)  # User's name from profile
    image = serializers.SerializerMethodField()  # User's image with presigned URL

    class Meta:
        model = User
        fields = ['block_id', 'user_id', 'email', 'name', 'image', 'reason']  # Fields to include in the response

    def get_block_id(self, obj):
        # `obj` is the blocked user; fetch the Block relationship
        request_user = self.context['request'].user
        try:
            block = Block.objects.get(blocker=request_user, blocked=obj)
            return block.id  # Return the block ID
        except Block.DoesNotExist:
            return None

    def get_reason(self, obj):
        # `obj` is the blocked user; fetch the reason from the Block model
        request_user = self.context['request'].user
        try:
            block = Block.objects.get(blocker=request_user, blocked=obj)
            return block.reason
        except Block.DoesNotExist:
            return None

    def get_image(self, obj):
        # Fetch the user's profile image and generate a presigned URL
        profile = obj.profile
        if profile.images:
            # Assuming the first image is the profile picture
            return get_presigned_url(profile.images[0])
        return None  # Return None if no image exists
    
class UserWithBlockStatusSerializer(serializers.ModelSerializer):
    isBlocked = serializers.SerializerMethodField()  # Custom field for block status
    name = serializers.CharField(source='profile.name', read_only=True)  # User's name from profile
    image = serializers.SerializerMethodField()  # User's image with presigned URL

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'image', 'isBlocked']  # Include `isBlocked` and user details

    def get_isBlocked(self, obj):
        # Check if the user is blocked by the current user
        request_user = self.context['request'].user
        return Block.objects.filter(blocker=request_user, blocked=obj).exists()

    def get_image(self, obj):
        # Fetch the user's profile image and generate a presigned URL
        profile = obj.profile
        if profile.images:
            # Assuming the first image is the profile picture
            return get_presigned_url(profile.images[0])
        return None  # Return None if no image exists
