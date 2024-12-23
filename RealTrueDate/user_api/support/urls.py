from django.urls import path
from .views import AboutUsView, ContactUsView, FAQView, PrivacyPolicyView, FeedbackView, SocialMediaView

urlpatterns = [
     path('about/', AboutUsView.as_view(), name='about'),
     path('faq/', FAQView.as_view(), name='faq'),
     path('faq/<int:pk>/', FAQView.as_view(), name='faq_detail'),
     path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
     path('contact/', ContactUsView.as_view(), name='contact'),
     path('feedback/', FeedbackView.as_view(), name='feedback'),
     path('social-media/', SocialMediaView.as_view(), name='social_media'),
     path('social-media/<int:pk>/', SocialMediaView.as_view(), name='social_media_detail'),
]
