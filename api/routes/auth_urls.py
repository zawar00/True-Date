from django.urls import path
from api.views.auth_view import (
    RegistrationView,
    OTPVerificationView,
    LoginView,
    PasswordResetRequestView,
    PasswordResetVerifyView,
    PasswordResetView,
    PasswordChangeView,
    CustomTokenRefreshView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('verify-otp/', OTPVerificationView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh-token/', CustomTokenRefreshView.as_view(), name='refresh-token'),
    path('request-password-reset/', PasswordResetRequestView.as_view(), name='request-password-reset'),
    path('verify-password-reset-otp/', PasswordResetVerifyView.as_view(), name='verify-password-reset-otp'),
    path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),  # Consider if you want to rename this
]
