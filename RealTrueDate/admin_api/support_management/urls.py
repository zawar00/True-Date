from django.urls import path
from .views import (
    FAQView,
    AboutUsView,
    PrivacyPolicyView,
    ContactUsView,
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
]
