from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, VerifyOTPView, LoginView, ChangePasswordView, PasswordResetRequestView, PasswordResetView, ResendOTPView
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('request-password-reset/', PasswordResetRequestView.as_view(), name='request_password_reset'),
    path('verify-password-reset-otp/', PasswordResetView.as_view(), name='verify_password_reset_otp'),
    path('refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('logout/', LogoutView.as_view(), name='logout'),
]
