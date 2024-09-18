from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

class UserRegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    gender = serializers.CharField(required=True)
    bio = serializers.CharField(required=True)
    looking_for = serializers.CharField(required=True)
    zipcode = serializers.CharField(required=True)
    birthday = serializers.DateField(required=True)
    distance = serializers.IntegerField(required=True)

class EmailTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Try to find the user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed({
                "email": ["No user found with this email address."]
            })

        # Authenticate the user using the username and password
        user = authenticate(username=user.username, password=password)

        if user is None:
            raise AuthenticationFailed({
                "password": ["Incorrect password."]
            })

        # Create token manually
        refresh = RefreshToken.for_user(user)

        # Return the refresh and access tokens
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }