from rest_framework import serializers
from api.models.user_profile import UserProfile, CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name', 'role', 'is_active', 'time_zone', 'device_id']

class UserProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()  # Nested serializer to include user details

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'dob', 'gender', 'interested_in', 'bio', 'location', 'willing_to_drive']

    # Override update method to handle user fields and profile fields
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()

        # Update user fields if present
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        return instance