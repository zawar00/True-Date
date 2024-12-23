from rest_framework.exceptions import ValidationError
from django.utils import timezone
from user_api.matching.models import Swipe
from user_api.users.models import User, UserProfile
from user_api.profiles.models import Block
from admin_api.transaction_management.models import Subscription
from datetime import datetime, timedelta
from django.utils.timezone import now


def check_required_fields(data, required_fields):
    """
    Utility function to check if the required fields are present in the data.
    :param data: The data (usually request.data or validated_data).
    :param required_fields: A list of required field names to check in the data.
    :raises ValidationError: If any required fields are missing, it raises a ValidationError.
    """
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
def calculate_age(dob):
    # Ensure dob is a datetime object, if it's a string, convert it first
    if isinstance(dob, str):
        dob = datetime.strptime(dob, "%Y-%m-%d")  # Adjust the format based on your dob format

    today = datetime.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    return age

def get_remaining_swipes(user):
    """
    Get the remaining swipe count for a user based on their free monthly swipes,
    subscription plan, and swipe usage.

    Args:
        user (User): The user whose remaining swipes we want to calculate.

    Returns:
        int or float('inf'): The remaining swipe count if the plan is limited,
                              or float('inf') if the plan has unlimited swipes.
    """
    try:
        # Fetch the user's profile to retrieve the monthly free swipes limit
        user_profile = UserProfile.objects.get(user=user)
        monthly_free_swipes = user_profile.free_swipes  # Dynamically get the value

        # Get the current month and year
        current_date = now()
        start_of_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

        # Fetch the number of swipes the user has made this month
        swipe_count_this_month = Swipe.objects.filter(
            user_id=user,
            timestamp__gte=start_of_month,
            timestamp__lte=end_of_month
        ).count()

        # Calculate remaining free swipes for the month
        remaining_free_swipes = max(monthly_free_swipes - swipe_count_this_month, 0)

        # If there are free swipes remaining, return them
        if remaining_free_swipes > 0:
            return remaining_free_swipes

        # Track when free swipes were exhausted
        free_swipes_exhausted_at = None
        if remaining_free_swipes <= 0:
            last_free_swipe = Swipe.objects.filter(
                user_id=user,
                timestamp__gte=start_of_month,
                timestamp__lte=end_of_month
            ).order_by('-timestamp').first()
            if last_free_swipe:
                free_swipes_exhausted_at = last_free_swipe.timestamp

        # Fetch the active subscription for the user
        active_subscription = Subscription.objects.filter(
            user=user,
            status='active',
            end__gte=current_date  # Ensure the subscription is still valid
        ).first()

        # If no active subscription, return 0 (no remaining swipes)
        if not active_subscription:
            return 0

        # Check if the plan has unlimited swipes
        if active_subscription.plan.has_unlimited_swipes:
            return float('inf')  # Unlimited swipes

        # Get the total number of swipes the user has made during the subscription period
        swipe_count = get_swipes_during_subscription(user, active_subscription, free_swipes_exhausted_at)

        # Get the subscription plan's swipe limit
        swipe_limit = active_subscription.plan.swipe_limit

        # Calculate remaining swipes
        remaining_swipes = swipe_limit - swipe_count

        # Ensure the remaining swipes do not go below zero
        return max(remaining_swipes, 0)

    except UserProfile.DoesNotExist:
        # If the user profile does not exist, return 0
        return 0
    except Exception as e:
        # Handle any unexpected errors gracefully
        return 0  # If an error occurs, treat it as 0 remaining swipes


def get_swipes_during_subscription(user, active_subscription, free_swipes_exhausted_at=None):
    """
    Get the number of swipes a user has made within the active subscription period.

    Args:
        user (User): The user whose swipes during the subscription period are to be calculated.
        active_subscription (Subscription): The active subscription object.
        free_swipes_exhausted_at (datetime, optional): The timestamp when free swipes were exhausted.

    Returns:
        int: The number of swipes made by the user during the active subscription period, or 0 if no active subscription.
    """
    try:
        # Get the start and end times of the subscription
        subscription_start = active_subscription.start
        subscription_end = active_subscription.end

        # Use the later of subscription start or free swipes exhausted timestamp
        effective_start = max(subscription_start, free_swipes_exhausted_at) if free_swipes_exhausted_at else subscription_start

        # Filter swipes by the effective subscription start and end times
        swipe_count = Swipe.objects.filter(
            user_id=user,
            timestamp__gte=effective_start,  # Swipes after the free swipes exhausted or subscription start
            timestamp__lte=subscription_end  # Swipes before the subscription end
        ).count()

        return swipe_count
    except Exception:
        return 0  # Return 0 on any error
 
def get_filtered_users(request):
    # Get IDs of users blocked by the current user
    blocked_ids = Block.objects.filter(blocker=request.user).values_list('blocked_id', flat=True)

    # Get IDs of users who have blocked the current user
    blocked_by_others_ids = Block.objects.filter(blocked=request.user).values_list('blocker_id', flat=True)

    # Exclude these users from the query
    users = User.objects.exclude(id__in=blocked_ids).exclude(id__in=blocked_by_others_ids)

    return users