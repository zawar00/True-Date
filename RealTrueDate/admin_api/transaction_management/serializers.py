from rest_framework import serializers
from .models import SubscriptionPlan, Subscription
from user_api.users.models import User, UserProfile
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

    class Meta:
        model = UserProfile
        fields = ['user', 'name', 'phone', 'zip_code', 'is_active', 'images',]
        read_only_fields = ['is_active']
        
    def to_representation(self, instance):
        """Override to dynamically generate pre-signed URLs for output."""
        representation = super().to_representation(instance)

        # Safely handle None values for images and videos
        representation['images'] = [
            get_presigned_url(image_key) for image_key in (instance.images or [])
        ]

        return representation

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer()  # Nested serializer for plan details
    user_profile = UserProfileSerializer(source='user.profile', read_only=True)  # Add user profile details

    class Meta:
        model = Subscription
        fields = [
            "id",
            "plan",
            "stripe_subscription_id",
            "status",
            "start",
            "end",
            "created_at",
            "updated_at",
            "user_profile",  # Explicitly add user_profile to fields
        ]
