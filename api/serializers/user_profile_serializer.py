from rest_framework import serializers
from api.models import UserProfile
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Django's built-in User model.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model, which includes additional user information.
    """
    user = UserSerializer(read_only=True)  # Nested serializer for User data

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'bio', 'age', 'gender', 'location', 'profile_picture', 'role', 
            'zipcode', 'birthday', 'looking_for', 'distance'
        ]

    def update(self, instance, validated_data):
        """
        Custom update method to handle nested user data.
        """
        # Handle nested user data (if any)
        user_data = self.context['request'].data.get('user', {})
        user = instance.user
        
        # Update User fields
        user.username = user_data.get('username', user.username)
        user.email = user_data.get('email', user.email)
        user.save()

        # Update UserProfile fields
        instance.bio = validated_data.get('bio', instance.bio)
        instance.age = validated_data.get('age', instance.age)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.location = validated_data.get('location', instance.location)
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.role = validated_data.get('role', instance.role)
        
        # Update new fields
        instance.zipcode = validated_data.get('zipcode', instance.zipcode)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.looking_for = validated_data.get('looking_for', instance.looking_for)
        instance.distance = validated_data.get('distance', instance.distance)

        instance.save()
        
        return instance
