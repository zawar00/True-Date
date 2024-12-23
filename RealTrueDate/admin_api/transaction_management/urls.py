from django.urls import path
from .views import SubscriptionPlanView, SubscriptionView, UserPaymentMethodsView

urlpatterns = [
    path('plans/', SubscriptionPlanView.as_view(), name='subscription-plans'),
    path('plans/<int:plan_id>/', SubscriptionPlanView.as_view(), name='get-plan-by-id'),
    path('subscriptions/', SubscriptionView.as_view(), name='create-subscription'),
    path('subscriptions/<int:subscription_id>/', SubscriptionView.as_view(), name='get_subscription_by_id'),
    path('subscriptions/user/', SubscriptionView.as_view(), name='get_user_subscriptions'),
    path('subscriptions/cancel/<int:subscription_id>/', SubscriptionView.as_view, name='cancel-subscription'),
    path('subscriptions/user/payment-methods/', UserPaymentMethodsView.as_view(), name='get_user_payment_methods'),
]
