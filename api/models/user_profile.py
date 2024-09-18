from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    A model that extends the default Django User model to store additional profile information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)  # User's gender
    location = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('user', 'User')], default='user')

    # New fields based on the registration form
    zipcode = models.CharField(max_length=10, blank=True, null=True)  # User's zipcode
    birthday = models.DateField(null=True, blank=True)  # User's birthday
    looking_for = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], blank=True)  # Who the user is looking for
    distance = models.PositiveIntegerField(null=True, blank=True)  # How far the user is willing to drive (in miles or km)
    
    def __str__(self):
        return self.user.username

# Signal to automatically create or save UserProfile when a User is created or updated
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()
