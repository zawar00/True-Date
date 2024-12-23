from django.urls import path
from .views import SubscriptionView, SubscriptionPlanView, UserPaymentMethodsView

urlpatterns = [
     path('', SubscriptionView.as_view(), name='subscription'),
     path('<int:subscription_id>/', SubscriptionView.as_view(), name='subscription_detail'),
     path('plans/', SubscriptionPlanView.as_view(), name='subscription_plans'),
     path('plans/<int:plan_id>/', SubscriptionPlanView.as_view(), name='subscription_plan_detail'),
     path('payment-methods/', UserPaymentMethodsView.as_view(), name='payment_methods'),
]