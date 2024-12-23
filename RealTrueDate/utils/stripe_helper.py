import stripe
from admin_api.transaction_management.models import SubscriptionPlan, Subscription
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_plan(data):
    """Create a Stripe product and price for the subscription plan."""
    try:
        # Retrieve price from the data, ensure it's a valid number
        price = int(data.get('price', None))
        if price is None or not isinstance(price, (int, float)):
            raise ValueError("Price must be a valid number.")
        
        # Convert price to cents (Stripe expects prices in the smallest unit, i.e., cents)
        price_in_cents = int(price * 100)
        
        # Check if the price exceeds the maximum allowed amount
        if price_in_cents > 1000000000:
            raise ValueError("Price exceeds the maximum allowed amount.")
        
        # Create a product on Stripe
        product = stripe.Product.create(
            name=data['name'],
            description=data.get('description', '')  # Optional
        )
        
        # Create a recurring price for the product
        stripe_price = stripe.Price.create(
            unit_amount=price_in_cents,
            currency=data.get('currency', 'usd'),
            recurring={"interval": data['interval']},  # e.g., "month", "year"
            product=product.id,
        )
        
        # Return the Stripe product and price IDs
        return product.id, stripe_price.id

    except ValueError as e:
        raise Exception(f"Invalid value for price: {str(e)}")

    except Exception as e:
        raise Exception(f"Error creating Stripe plan: {str(e)}")

def cancel_stripe_subscription(subscription_id):
    try:
        stripe.Subscription.delete(subscription_id)
    except Exception as e:
        raise Exception(f"Error cancelling Stripe subscription: {str(e)}")

def get_stripe_subscription(subscription_id):
    try:
        return stripe.Subscription.retrieve(subscription_id)
    except Exception as e:
        raise Exception(f"Error retrieving Stripe subscription: {str(e)}")

def get_stripe_payment_methods(customer_id):
    try:
        return stripe.PaymentMethod.list(
            customer=customer_id, type="card"
        ).data
    except Exception as e:
        raise Exception(f"Error retrieving payment methods: {str(e)}")
    
def get_or_create_stripe_customer(user):
    """Retrieve or create a Stripe customer."""
    try:
        # Check if a Stripe customer already exists for the user
        customers = stripe.Customer.list(email=user.email)
        if customers.data:
            return customers.data[0]  # Return the first matching customer
        else:
            # Create a new Stripe customer if not found
            return stripe.Customer.create(
                email=user.email,
                name=user.get_full_name()
            )
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe customer creation failed: {e.user_message}")

def attach_payment_method_to_customer(customer_id, payment_method_id):
    """Attach a payment method to the Stripe customer."""
    try:
        # Attach the payment method to the customer
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id,
        )
        # Set the payment method as the default for future payments
        stripe.Customer.modify(
            customer_id,
            invoice_settings={"default_payment_method": payment_method_id},
        )
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to attach payment method: {e.user_message}")

def create_stripe_subscription(customer_id, price_id, trial_period_days=None):
    """Create a Stripe subscription."""
    try:
        subscription_data = {
            "customer": customer_id,
            "items": [{"price": price_id}],
        }

        if trial_period_days:
            trial_end = int((timezone.now() + timedelta(days=trial_period_days)).timestamp())
            subscription_data['trial_end'] = trial_end

        subscription = stripe.Subscription.create(**subscription_data)
        return subscription
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe subscription creation failed: {e.user_message}")

def get_subscription_plan(plan_id):
    """Get a subscription plan by ID."""
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        return plan
    except SubscriptionPlan.DoesNotExist:
        raise Exception("Plan not found or inactive")

def cancel_stripe_subscription(stripe_subscription_id):
    try:
        stripe.Subscription.delete(stripe_subscription_id)
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe Error: {e.user_message}")  # Custom error handling for Stripe
    
def get_payment_methods(user_email):
    try:
        # Retrieve the customer ID from your system (ensure user_email is associated with Stripe customer)
        customer = stripe.Customer.list(email=user_email).data

        if not customer:
            raise Exception("No Stripe customer found with this email.")

        # Retrieve the payment methods associated with the Stripe customer
        payment_methods = stripe.PaymentMethod.list(
            customer=customer[0].id,
            type="card"
        )
        
        return payment_methods.data  # Return the list of payment methods
    
    except Exception as e:
        raise Exception(f"Error fetching payment methods: {str(e)}")

def get_user_active_subscription(user):
    """
    Fetch and return active subscription details for a given user.
    
    Args:
        user (User): The user object for whom the subscription is to be retrieved.
    
    Returns:
        dict: A dictionary containing the subscription details or None if no active subscription.
    """
    # Fetch the active subscription (status='active' and end date > current date)
    active_subscription = Subscription.objects.filter(
        user=user,
        status='active',
        end__gte=timezone.now()  # Check if the subscription end date is in the future
    ).first()

    if active_subscription:
        plan = active_subscription.plan  # Get the related subscription plan
        return {
            "plan": plan.name,  # Subscription plan name
            "price": plan.price,  # Subscription plan price
            "currency": plan.currency,  # Currency of the price
            "interval": plan.interval,  # Billing interval (e.g., month, year)
            "status": active_subscription.status,  # Subscription status (active, trialing, canceled)
            "expiry_date": active_subscription.end,  # Expiry date (end of the subscription)
            "features": plan.features,  # List of features available in the subscription
            "has_unlimited_swipes": plan.has_unlimited_swipes,  # Flag for unlimited swipes
            "swipe_limit": plan.swipe_limit,  # Remaining swipe count
        }

    # If no active subscription found
    return None