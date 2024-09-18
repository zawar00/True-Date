from django.contrib.auth.models import User
from api.models.user_profile import UserProfile
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError

def register_user(data):
    """
    Handles the registration of a new user along with the creation of their profile.
    """
    # Extract data
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    gender = data.get('gender')
    bio = data.get('bio')
    looking_for = data.get('looking_for')
    zipcode = data.get('zipcode')
    birthday = data.get('birthday')
    distance = data.get('distance')

    # Check if the email is already registered
    if User.objects.filter(email=email).exists():
        raise ValidationError("Email is already registered.")

    # Create the user
    user = User.objects.create(
        username=email,  # assuming email as username
        email=email,
        password=make_password(password),  # hash the password
        first_name=name
    )

    # Create the user profile
    UserProfile.objects.create(
        user=user,
        gender=gender,
        bio=bio,
        looking_for=looking_for,
        zipcode=zipcode,
        birthday=birthday,
        distance=distance
    )

    return user
