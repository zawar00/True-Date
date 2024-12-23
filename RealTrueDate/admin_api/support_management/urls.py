from django.urls import path
from .views import (
    FAQView,
    AboutUsView,
    PrivacyPolicyView,
    ContactUsView,
    SocialMediaView,
    FeedbackView,
    BlockedUserView
)

urlpatterns = [
    # FAQ Endpoints
    path('faq/', FAQView.as_view(), name='faq-list-create'),
    path('faq/<int:pk>/', FAQView.as_view(), name='faq-detail'),
    path('faq/<int:pk>/toggle-status/', FAQView.as_view(), name='faq-toggle-status'),

    # About Us Endpoint
    path('about-us/', AboutUsView.as_view(), name='about-us'),

    # Privacy Policy Endpoint
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),

    # Ask Anything Endpoints
    path('contact-us/', ContactUsView.as_view(), name='contact-us-list-create'),  # List and Create
    path('contact-us/<int:pk>/', ContactUsView.as_view(), name='contact-us-detail'),  # Retrieve, Update, Delete
    path('contact-us/<int:pk>/toggle-replied/', ContactUsView.as_view(), name='contact-us-mark-replied'),  # Mark as Replied

    # Social Media Endpoints
    path('social-media/', SocialMediaView.as_view(), name='get_create_social_media'),  # For GET and POST
    path('social-media/<int:pk>/', SocialMediaView.as_view(), name='get_create_social_media'),  # For GET By id
    path('social-media/<int:pk>/status/', SocialMediaView.as_view(), name='toggle_status'),  # Toggle is_active status
    path('social-media/<int:pk>/update/', SocialMediaView.as_view(), name='update_social_media_details'),
    path('social-media/<int:pk>/delete', SocialMediaView.as_view(), name='update_delete_social_media'),  # For PUT and DELETE

    # Feedback Endpoints
    path('feedback/', FeedbackView.as_view(), name='feedback-list-create'),  # List and Create
    path('feedback/<int:pk>/', FeedbackView.as_view(), name='feedback-detail'),  # Retrieve, Update, Delete
    path('feedback/<int:pk>/toggle-replied/', FeedbackView.as_view(), name='feedback-mark-replied'),  # Mark as Replied

    # Blocked User Endpoint
    path('blocked-users/', BlockedUserView.as_view(), name='blocked-user'),
    path('blocked-users/<int:blocked_user_id>', BlockedUserView.as_view(), name='blocked-user'),


]
