from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .models import SubscriptionPlan, Subscription
from .serializers import SubscriptionPlanSerializer, SubscriptionSerializer
from utils.stripe_helper import create_stripe_plan, create_stripe_subscription, cancel_stripe_subscription, get_subscription_plan, get_or_create_stripe_customer, attach_payment_method_to_customer, cancel_stripe_subscription, get_payment_methods
from django.contrib.auth.models import User
from utils.response_helper import successResponse, errorResponse
from utils.permissions import IsAdminUser, IsRegularUser
from utils.helper import check_required_fields
from django.utils import timezone
from django.shortcuts import get_object_or_404


class SubscriptionPlanView(APIView):
     def get_permissions(self):
        """Return the permission classes based on the action."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

     def post(self, request):
        """Create a subscription plan and a corresponding Stripe plan."""
        data = request.data
        required_fields = ['name', 'description', 'price', 'interval', 'has_unlimited_swipes']

        try:
            # Check if required fields are present
            check_required_fields(data, required_fields)

            # Check if a plan with the same name already exists
            existing_plan = SubscriptionPlan.objects.filter(name=data['name']).first()
            if existing_plan:
                return errorResponse(message="A plan with this name already exists.", code=status.HTTP_400_BAD_REQUEST)
            
            # Create Stripe plan first
            stripe_product_id, stripe_price_id = create_stripe_plan(data)

            # Create the subscription plan
            plan = SubscriptionPlan.objects.create(
                name=data['name'],
                description=data['description'],
                price=data['price'],
                currency=data.get('currency', 'usd'),
                interval=data['interval'],
                trial_period_days=data.get('trial_period_days', 0),
                features=data.get('features', []),
                has_unlimited_swipes=data.get('has_unlimited_swipes', False),  # Check for unlimited swipes
                swipe_limit=data.get('swipe_limit', None),  # Set swipe limit if not unlimited
                stripe_product_id=stripe_product_id,  # Stripe product ID
                stripe_price_id=stripe_price_id,  # Stripe price ID
                created_by=request.user  # Set the user who created the plan
            )

            return successResponse(data=SubscriptionPlanSerializer(plan).data, message="Plan created successfully.", code=status.HTTP_201_CREATED)

        except ValidationError as e:
            return errorResponse(message=str(e), code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return errorResponse(message=str(e), code=status.HTTP_400_BAD_REQUEST)
       
     def put(self, request, plan_id):
        """Toggle active/inactive status of a plan."""
        try:
            # Fetch the subscription plan based on ID and user
            plan = SubscriptionPlan.objects.get(id=plan_id)
            
            # Toggle the 'is_active' status
            plan.is_active = not plan.is_active
            plan.save()

            # Return appropriate success response
            status_message = "Plan activated successfully." if plan.is_active else "Plan deactivated successfully."
            return successResponse(message=status_message, code=status.HTTP_204_NO_CONTENT)

        except SubscriptionPlan.DoesNotExist:
            return errorResponse(message="Plan not found.", code=status.HTTP_404_NOT_FOUND) 
       
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
    permission_classes = [IsAdminUser]

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
            # if request.user.is_authenticated:
            #     # Fetch user subscriptions
            #     subscriptions = Subscription.objects.filter(user=request.user)
                
            #     if not subscriptions.exists():
            #         return errorResponse(message="No subscriptions found", code=status.HTTP_404_NOT_FOUND)

            #     # Serialize subscriptions
            #     subscriptions_data = SubscriptionSerializer(subscriptions, many=True).data
            #     return successResponse(
            #         data=subscriptions_data,
            #         message="User's subscriptions retrieved successfully.",
            #         code=status.HTTP_200_OK
            #     )
            
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
            subscription = get_object_or_404(Subscription, id=subscription_id)

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
    permission_classes = [IsAdminUser]  # Ensure the user is authenticated

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
