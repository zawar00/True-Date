from rest_framework import serializers
from .models import FAQ, AboutUs, PrivacyPolicy, ContactUs, SocialMedia, Feedback
from user_api.profiles.models import Block
from user_api.users.models import User
from utils.uploadFiles import get_presigned_url

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = '__all__'

class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = '__all__'

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['id', 'username', 'email', 'message', 'reply', 'replied']

class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = ['id', 'title', 'url', 'icon', 'is_active']
        read_only_fields = ['id', 'is_active']

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'username', 'email', 'description', 'rating', 'reply', 'replied']

class UserDetailSerializer(serializers.ModelSerializer):
    """Nested serializer for user details."""
    name = serializers.CharField(source='profile.name', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'image']

    def get_image(self, obj):
        # Fetch the user's profile image and generate a presigned URL
        profile = obj.profile
        if profile.images:
            return get_presigned_url(profile.images[0])
        return None


class BlockDetailSerializer(serializers.ModelSerializer):
    """Serializer to display block details including blocker and blocked users."""
    blocker = UserDetailSerializer(read_only=True)  # Serialize blocker user details
    blocked = UserDetailSerializer(read_only=True)  # Serialize blocked user details

    class Meta:
        model = Block
        fields = ['id', 'blocker', 'blocked', 'reason', 'created_at']  # Fields to include in the response