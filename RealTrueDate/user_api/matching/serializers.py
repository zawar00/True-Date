# serializers.py

from rest_framework import serializers
from .models import Swipe
from user_api.profiles.models import Block
from utils.uploadFiles import get_presigned_url

class SwipeSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)  # Include the user's ID
    target_user_id = serializers.IntegerField(source='target_user.id', read_only=True)  # Target user's ID
    target_user_name = serializers.CharField(source='target_user.profile.name', read_only=True)  # Target user's name
    target_user_image = serializers.SerializerMethodField()  # Dynamically get target user's image
    isBlocked = serializers.SerializerMethodField()  # Dynamically calculate block status

    class Meta:
        model = Swipe
        fields = [
            'user_id',
            'target_user_id',
            'target_user_name',
            'target_user_image',
            'direction',
            'timestamp',
            'isBlocked'
        ]

    def get_target_user_image(self, obj):
        """
        Fetch the first image of the target user from their profile and generate a presigned URL.
        """
        try:
            profile = obj.target_user.profile
            if profile.images:
                # Assuming the first image in the list is the profile picture
                return get_presigned_url(profile.images[0])
        except AttributeError:
            return None  # Return None if no images are available or profile is missing

    def get_isBlocked(self, obj):
        """
        Check if the `target_user` is blocked by the `user` making the request.
        """
        request_user = obj.user
        try:
            # Check if the request user has blocked the target user
            return Block.objects.filter(blocker=request_user, blocked=obj.target_user).exists()
        except Exception:
            return False  # Default to False if any error occurs