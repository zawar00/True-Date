from django.contrib.auth.models import AbstractUser, Group, Permission
# from django.db import models
from django.contrib.gis.db import models
from datetime import date
from django.contrib.gis.geos import Point

class User(AbstractUser):
    email = models.EmailField(unique=True)
    time_zone = models.CharField(max_length=50, null=True, blank=True)
    user_role = models.CharField(max_length=20, choices=[('user', 'User'), ('admin', 'Admin')], default='user')
    is_verified = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10,
        choices=[('inactive', 'Inactive'), ('active', 'Active'), ('deleted', 'Deleted')],
        default='inactive'
    )

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Automatically verify admins
        if self.user_role == 'admin' and not self.is_verified:
            self.is_verified = True
            self.status = 'active'
        super(User, self).save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, unique=False, null=True, blank=True)
    age_min = models.IntegerField(default=18, null=True, blank=True, help_text="Minimum age for the user's interest")
    age_max = models.IntegerField(null=True, blank=True, help_text="Maximum age for the user's interest", default=35)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    interested_in = models.CharField(max_length=10)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    location = models.JSONField()
    location_point = models.PointField(null=True, blank=True, default=Point(0, 0))  # Use PointField for geospatial location
    willing_to_drive = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    images = models.JSONField(default=list)
    videos = models.JSONField(default=list)
    free_swipes = models.IntegerField(default=5, help_text="Number of free swipes available") 

    class Meta:
        indexes = [
            models.Index(fields=['location_point']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def age(self):
        """Calculate age from dob (Date of Birth)."""
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    def save(self, *args, **kwargs):
        """Override save method to automatically update the location_point."""
        if self.location and isinstance(self.location, dict):
            lat = self.location.get("lat")
            lng = self.location.get("lng")
            if lat is not None and lng is not None:
                # Create a Point object for the location_point
                self.location_point = Point(lng, lat)
        super(UserProfile, self).save(*args, **kwargs)


# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
#     name = models.CharField(max_length=255, blank=True, null=True)
#     phone = models.CharField(max_length=15, unique=False, null=True, blank=True)
#     dob = models.DateField()
#     gender = models.CharField(max_length=10)
#     interested_in = models.CharField(max_length=10)
#     location = models.JSONField()
#     location_point = models.PointField(null=True, blank=True)  # Use PointField for geospatial location
#     willing_to_drive = models.DecimalField(max_digits=5, decimal_places=2)
#     is_active = models.BooleanField(default=True)
#     images = models.JSONField(default=list)
#     videos = models.JSONField(default=list)

#     def __str__(self):
#         return f"{self.user.username}'s Profile"

#     @property
#     def age(self):
#         """Calculate age from dob (Date of Birth)."""
#         today = date.today()
#         return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)

class UserDeviceSession(models.Model):  # Renamed to UserDeviceSession for clarity
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="device_sessions")
    device_id = models.CharField(max_length=100)  # Unique identifier for each device session
    refresh_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.email} - {self.device_id}"