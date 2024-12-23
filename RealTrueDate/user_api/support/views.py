from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from admin_api.support_management.models import FAQ, AboutUs, PrivacyPolicy, SocialMedia
from .serializers import FAQSerializer, AboutUsSerializer, PrivacyPolicySerializer, ContactUsSerializer, SocialMediaSerializer, FeedbackSerializer
from utils.response_helper import successResponse, errorResponse

class FAQView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Retrieve a list of FAQs or a specific FAQ based on the presence of `pk`.
        """
        pk = kwargs.get('pk')
        if pk:
            # Retrieve a specific FAQ
            try:
                faq = FAQ.objects.get(pk=pk, is_active=True)
                serializer = FAQSerializer(faq)
                return successResponse(data=serializer.data, message="FAQ retrieved successfully.")
            except FAQ.DoesNotExist:
                return errorResponse(message="FAQ not found.", code=status.HTTP_404_NOT_FOUND)
        else:
            # Retrieve all FAQs
            faqs = FAQ.objects.filter(is_active=True)
            serializer = FAQSerializer(faqs, many=True)
            return successResponse(data=serializer.data, message="FAQs retrieved successfully.")

# About Us API
class AboutUsView(APIView):
    """
    Single-instance view for About Us content.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Retrieve the About Us content.
        """
        about_us = AboutUs.objects.first()
        if not about_us:
            return errorResponse(message="About Us content not found.", code=status.HTTP_404_NOT_FOUND)
        serializer = AboutUsSerializer(about_us)
        return successResponse(data=serializer.data, message="About Us retrieved successfully.")
    
class PrivacyPolicyView(APIView):
    """
    Single-instance view for Privacy Policy content.
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Retrieve the Privacy Policy content.
        """
        privacy_policy = PrivacyPolicy.objects.first()
        if not privacy_policy:
            return errorResponse(message="Privacy Policy content not found.", code=status.HTTP_404_NOT_FOUND)
        serializer = PrivacyPolicySerializer(privacy_policy)
        return successResponse(data=serializer.data, message="Privacy Policy retrieved successfully.")
    
class ContactUsView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ContactUsSerializer

    def post(self, request, *args, **kwargs):
        """
        Create a new message.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return successResponse(data=serializer.data, message="Message submitted successfully.", code=status.HTTP_201_CREATED)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)
    
# Feedback API
class FeedbackView(APIView):
    permission_classes = [AllowAny]
    serializer_class = FeedbackSerializer

    def post(self, request, *args, **kwargs):
        """
        Create a new message.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return successResponse(data=serializer.data, message="Feedback submitted successfully.", code=status.HTTP_201_CREATED)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)
    
class SocialMediaView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        """
        Get all social media links or filter by active status or get by id.
        """
        if pk:
            # If pk (ID) is provided, return the specific social media link
            try:
                social_media = SocialMedia.objects.get(pk=pk, is_active=True)
            except SocialMedia.DoesNotExist:
                return errorResponse(message="Social media link not found", code=status.HTTP_404_NOT_FOUND)

            serializer = SocialMediaSerializer(social_media)
            return successResponse(data=serializer.data, message="Social media link retrieved successfully", code=status.HTTP_200_OK)
        
        social_media = SocialMedia.objects.filter(is_active=True)

        serializer = SocialMediaSerializer(social_media, many=True)
        return successResponse(data=serializer.data, message="Social media links retrieved successfully", code=status.HTTP_200_OK)
