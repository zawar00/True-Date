from api.models import UserProfile
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

def get_user_profile_by_id(pk):
    """
    Fetches the user profile by ID.
    """
    return UserProfile.objects.get(pk=pk)

def create_user_profile(data):
    """
    Creates a new UserProfile.
    """
    # Extract data from request
    user_data = data.get('user', {})
    username = user_data.get('username')
    email = user_data.get('email')
    password = user_data.get('password')
    
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        raise ValidationError("A user with this email already exists.")
    
    # Create User
    user = User.objects.create(username=username, email=email)
    user.set_password(password)
    user.save()

    # Create Profile
    profile = UserProfile.objects.create(
        user=user,
        bio=data.get('bio', ''),
        age=data.get('age'),
        gender=data.get('gender'),
        location=data.get('location'),
        zipcode=data.get('zipcode'),
        birthday=data.get('birthday'),
        looking_for=data.get('looking_for'),
        distance=data.get('distance')
    )
    return profile

def update_user_profile(pk, data):
    """
    Updates an existing UserProfile.
    """
    profile = UserProfile.objects.get(pk=pk)
    
    # Update profile fields
    profile.bio = data.get('bio', profile.bio)
    profile.age = data.get('age', profile.age)
    profile.gender = data.get('gender', profile.gender)
    profile.location = data.get('location', profile.location)
    profile.zipcode = data.get('zipcode', profile.zipcode)
    profile.birthday = data.get('birthday', profile.birthday)
    profile.looking_for = data.get('looking_for', profile.looking_for)
    profile.distance = data.get('distance', profile.distance)
    
    # Update User fields (optional)
    user_data = data.get('user', {})
    profile.user.username = user_data.get('username', profile.user.username)
    profile.user.email = user_data.get('email', profile.user.email)
    profile.user.save()
    
    profile.save()
    return profile
