from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email

        # Example: Add a custom role from the user profile (if it exists)
        if hasattr(user, 'profile'):
            token['role'] = user.profile.role  # Assuming UserProfile has a 'role' field

        return token
