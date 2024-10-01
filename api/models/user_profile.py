from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Automatically assign groups based on the user's role
        self.assign_default_group(user)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.SUPERADMIN)
        return self.create_user(email, password, **extra_fields)

    def assign_default_group(self, user):
        from django.contrib.auth.models import Group
        if user.role == CustomUser.ADMIN:
            admin_group, created = Group.objects.get_or_create(name='Admins')
            user.groups.add(admin_group)
        elif user.role == CustomUser.SUPERADMIN:
            superadmin_group, created = Group.objects.get_or_create(name='SuperAdmin')
            user.groups.add(superadmin_group)
        else:
            user_group, created = Group.objects.get_or_create(name='Users')
            user.groups.add(user_group)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ADMIN = 'Admin'
    SUPERADMIN = 'SuperAdmin'
    USER = 'User'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (SUPERADMIN, 'Super Admin'),
        (USER, 'User')
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=USER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Can log into Django admin
    is_superuser = models.BooleanField(default=False)  # Has full admin rights
    is_verified = models.BooleanField(default=False)
    time_zone = models.CharField(max_length=100, blank=True, null=True)
    device_id = models.CharField(max_length=255, blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_query_name="customuser",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    # Helper methods for roles
    def is_admin(self):
        return self.role == self.ADMIN

    def is_superadmin(self):
        return self.role == self.SUPERADMIN

    def is_regular_user(self):
        return self.role == self.USER
    
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10)
    interested_in = models.CharField(max_length=10)
    bio = models.TextField(blank=True)
    location = models.JSONField(blank=True, null=True)
    willing_to_drive = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.name}'s profile"

class UserOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)
