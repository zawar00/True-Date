from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.exceptions import ValidationError
from admin_api.transaction_management.models import SubscriptionPlan, Subscription
from .serializers import SubscriptionPlanSerializer, SubscriptionSerializer
from utils.stripe_helper import  create_stripe_subscription, cancel_stripe_subscription, get_subscription_plan, get_or_create_stripe_customer, attach_payment_method_to_customer, cancel_stripe_subscription, get_payment_methods
from utils.response_helper import successResponse, errorResponse
from utils.permissions import IsRegularUser
from utils.helper import check_required_fields
from django.utils import timezone
from django.shortcuts import get_object_or_404

class SubscriptionPlanView(APIView):
     permission_classes = [AllowAny]
  
     def get(self, request, plan_id=None):
          """Get a subscription plan by ID."""
          try:
               if plan_id is None:
                   plans = SubscriptionPlan.objects.all()
                   return successResponse(data=SubscriptionPlanSerializer(plans, many=True).data, message="Plans fetched successfully.", code=status.HTTP_200_OK)
               # Get the subscription plan by ID
               plan = SubscriptionPlan.objects.get(id=plan_id)
               return successResponse(data=SubscriptionPlanSerializer(plan).data, message="Plan fetched successfully.", code=status.HTTP_200_OK)
          except SubscriptionPlan.DoesNotExist:
               return errorResponse(message="Plan not found.", code=status.HTTP_404_NOT_FOUND)
          
class SubscriptionView(APIView):
    permission_classes = [IsRegularUser]

    def get(self, request, subscription_id=None):
        """
        Get a subscription by ID, all subscriptions, or user's subscriptions.
        - If `subscription_id` is provided, fetch subscription by ID.
        - Otherwise, fetch all subscriptions or user's subscriptions.
        """
        try:
            if subscription_id:
                # Get subscription by ID
                subscription = get_object_or_404(Subscription, id=subscription_id)
                subscription_data = SubscriptionSerializer(subscription).data
                return successResponse(
                    data=subscription_data,
                    message="Subscription retrieved successfully.",
                    code=status.HTTP_200_OK
                )
            
            # If no subscription_id is provided, check if it's a request for all or user's subscriptions
            if request.user.is_authenticated:
                # Fetch user subscriptions
                subscriptions = Subscription.objects.filter(user=request.user)
                
                if not subscriptions.exists():
                    return errorResponse(message="No subscriptions found", code=status.HTTP_404_NOT_FOUND)

                # Serialize subscriptions
                subscriptions_data = SubscriptionSerializer(subscriptions, many=True).data
                return successResponse(
                    data=subscriptions_data,
                    message="User's subscriptions retrieved successfully.",
                    code=status.HTTP_200_OK
                )
            
            # Fetch all subscriptions for admin or if no specific user
            subscriptions = Subscription.objects.all()
            subscriptions_data = SubscriptionSerializer(subscriptions, many=True).data
            return successResponse(
                data=subscriptions_data,
                message="Subscriptions retrieved successfully.",
                code=status.HTTP_200_OK
            )

        except Exception as e:
            return errorResponse(message=str(e), details=str(e), code=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """Create a subscription for the logged-in user."""
        user = request.user
        data = request.data
        required_fields = ['plan_id', 'payment_method_id']

        
        check_required_fields(data, required_fields)
        # Extract required parameters
        plan_id = data.get("plan_id")
        payment_method_id = data.get("payment_method_id")

        # Step 1: Retrieve the active subscription plan
        try:
            plan = get_subscription_plan(plan_id)
        except ValidationError as e:
           # Handle missing required fields
           return errorResponse(message=str(e), code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return errorResponse(message=str(e), code=status.HTTP_404_NOT_FOUND)

        # Step 2: Check if the user is already subscribed to this plan
        existing_subscription = Subscription.objects.filter(user=user, plan=plan, status__in=["active", "trialing"]).first()

        if existing_subscription:
            return errorResponse(message="You are already subscribed to this plan.", code=status.HTTP_400_BAD_REQUEST)

        try:
            # Step 3: Create or find Stripe customer by email
            customer = get_or_create_stripe_customer(user)

            # Step 4: Attach the payment method to the customer
            attach_payment_method_to_customer(customer.id, payment_method_id)

            # Step 5: Create the Stripe subscription
            subscription = create_stripe_subscription(customer.id, plan.stripe_price_id, plan.trial_period_days)

            # Step 6: Convert Stripe timestamps to Django datetime objects
            current_period_start = timezone.datetime.fromtimestamp(
                subscription["current_period_start"]
            )
            current_period_end = timezone.datetime.fromtimestamp(
                subscription["current_period_end"]
            )

            # Step 7: Save the subscription in the database
            subscription_obj = Subscription.objects.create(
                user=user,
                plan=plan,
                status=subscription["status"],
                stripe_subscription_id=subscription["id"],
                start=current_period_start,
                end=current_period_end,
            )

            # Step 8: Return successful response with subscription data
            return successResponse(
                data=SubscriptionSerializer(subscription_obj).data,
                message="Subscription created successfully.",
                code=status.HTTP_201_CREATED
            )

        except Exception as e:
            # Handle errors and return an appropriate response
            return errorResponse(message=str(e), code=status.HTTP_400_BAD_REQUEST)

    # The function to cancel the subscription in the database and Stripe
    def delete(self, request, subscription_id):
        """Cancel the subscription for the logged-in user."""
        user = request.user
        try:
            # Get the subscription from the database
            subscription = get_object_or_404(Subscription, id=subscription_id, user=user)

            # Cancel the subscription in Stripe
            cancel_stripe_subscription(subscription.stripe_subscription_id)

            # Update the subscription status to 'canceled' in the database
            subscription.status = 'canceled'
            subscription.save()

            # Return success response using your helper function
            return successResponse(data=SubscriptionSerializer(subscription).data, message="Subscription canceled successfully", code=200)

        except Subscription.DoesNotExist:
            return errorResponse(message="Subscription not found", code=404)
        except Exception as e:
            return errorResponse(message=str(e), details=str(e), code=400)

class UserPaymentMethodsView(APIView):
    permission_classes = [IsRegularUser]  # Ensure the user is authenticated

    def get(self, request):
        """Get the logged-in user's payment methods from Stripe."""
        try:
            user = request.user  # Get the logged-in user
            
            # Fetch payment methods from Stripe using the helper function
            payment_methods = get_payment_methods(user.email)
            
            # Return success response with payment methods
            return successResponse(
                data=payment_methods,
                message="Payment methods retrieved successfully",
                code=status.HTTP_200_OK
            )
        
        except Exception as e:
            # If there is an error, return an error response
            return errorResponse(message=str(e), details=str(e), code=status.HTTP_400_BAD_REQUEST)
