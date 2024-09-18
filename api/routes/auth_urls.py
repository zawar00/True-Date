from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api.views.auth_view import EmailLoginView, RegisterView  # Import the views

urlpatterns = [
    path('login/', EmailLoginView.as_view(), name='token_obtain_pair'),  # Custom JWT login
    path('register/', RegisterView.as_view(), name='register'),  # Registration endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh JWT token (optional)
]
