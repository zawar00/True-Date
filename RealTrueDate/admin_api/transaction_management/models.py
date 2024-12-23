from django.db import models
from user_api.users.models import User  # Assuming a built-in or custom User model
from django.utils.timezone import now

class SubscriptionPlan(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_plans")
    name = models.CharField(max_length=255)  # Name of the subscription plan
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price in the selected currency
    currency = models.CharField(max_length=10, default='usd')  # Default currency is USD
    interval = models.CharField(max_length=10, choices=[('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year')])  # Billing interval
    stripe_price_id = models.CharField(max_length=255, blank=False, null=False)  # Stripe Price ID
    stripe_product_id = models.CharField(max_length=255, blank=False, null=False)  # Stripe Product ID
    is_active = models.BooleanField(default=True)  # Plan status
    description = models.TextField(blank=True, null=True)  # Optional plan description
    features = models.JSONField(default=list, blank=True, null=True)  # Features stored as JSON
    trial_period_days = models.IntegerField(default=0)  # Number of trial days (if any)
    has_unlimited_swipes = models.BooleanField(default=False)  # Flag to indicate if plan has unlimited swipes
    swipe_limit = models.IntegerField(default=0)  # Swipe limit for limited plans

    created_at = models.DateTimeField(auto_now_add=True)  # Auto-populate on creation
    updated_at = models.DateTimeField(auto_now=True)  # Auto-update on modification

    def __str__(self):
        return self.name

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')  # Subscribed user
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions')  # Related subscription plan
    stripe_subscription_id = models.CharField(max_length=255, blank=False, null=False)  # Stripe Subscription ID
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('trialing', 'Trialing'), ('canceled', 'Canceled')])  # Subscription status
    start = models.DateTimeField(default=now)  # Start date
    end = models.DateTimeField()  # End date or expected renewal date
    
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-populate on creation
    updated_at = models.DateTimeField(auto_now=True)  # Auto-update on modification

    def save(self, *args, **kwargs):
        # Automatically set swipe_count to None for unlimited swipe plans
        if self.plan.has_unlimited_swipes:
            self.swipe_count = None  # Unlimited swipes
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Subscription: {self.user.email} - {self.plan.name}"

