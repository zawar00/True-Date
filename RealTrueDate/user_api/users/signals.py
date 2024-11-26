from django.db.models.signals import post_save
from django.dispatch import receiver
from user_api.users.models import User, UserProfile

@receiver(post_save, sender=User)
def create_demo_profile_for_admin(sender, instance, created, **kwargs):
    """
    Automatically create a demo profile for admin users after registration.
    """
    if created and instance.user_role == 'admin':
        UserProfile.objects.create(
            user=instance,
            name="Demo Admin",  # Default name
            phone="1234567890",  # Default phone
            dob="1980-01-01",  # Default DOB
            gender="N/A",  # Default gender
            interested_in="N/A",  # Default interest
            location= {
                "lat": 0.0,
                "lng": -0.0
                },
            willing_to_drive=False,  # Default driving preference
            is_active=True,  # Mark admin profiles as verified
            images= ["images/key1.jpg", "images/key2.png"],
            videos= ["videos/key1.mp4"]
        )
