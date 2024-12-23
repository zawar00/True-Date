from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from .models import FAQ, AboutUs, PrivacyPolicy, ContactUs, SocialMedia, Feedback
from user_api.profiles.models import Block
from user_api.users.models import User
from .serializers import FAQSerializer, AboutUsSerializer, PrivacyPolicySerializer, ContactUsSerializer, SocialMediaSerializer, FeedbackSerializer, BlockDetailSerializer
from utils.response_helper import successResponse, errorResponse
from utils.permissions import IsAdminUser


# class PublicReadAdminWritePermission:
#     """
#     Custom permission class that allows GET for everyone
#     but restricts POST, PUT, and DELETE to admin users.
#     """
#     def has_permission(self, request, view):
#         if request.method in ['GET', 'HEAD', 'OPTIONS']:
#             return True
#         return request.user and request.user.is_authenticated and request.user.is_admin


# FAQ API
class FAQView(APIView):
    def get_permissions(self):
        """
        Define permissions dynamically based on the request method.
        - GET: Allow anyone.
        - Other methods: Admin-only.
        """
        if self.request.method == 'GET':
            return [AllowAny()]  # Anyone can view FAQs
        return [IsAdminUser()]  # Only admins can modify FAQs

    def get(self, request, *args, **kwargs):
        """
        Retrieve a list of FAQs or a specific FAQ based on the presence of `pk`.
        """
        pk = kwargs.get('pk')
        if pk:
            # Retrieve a specific FAQ
            try:
                faq = FAQ.objects.get(pk=pk)
                serializer = FAQSerializer(faq)
                return successResponse(data=serializer.data, message="FAQ retrieved successfully.")
            except FAQ.DoesNotExist:
                return errorResponse(message="FAQ not found.", code=status.HTTP_404_NOT_FOUND)
        else:
            # Retrieve all FAQs
            faqs = FAQ.objects.all()
            serializer = FAQSerializer(faqs, many=True)
            return successResponse(data=serializer.data, message="FAQs retrieved successfully.")

    def post(self, request, *args, **kwargs):
        """
        Create a new FAQ (Admin-only).
        """
        serializer = FAQSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return successResponse(data=serializer.data, message="FAQ created successfully.", code=status.HTTP_201_CREATED)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        Update an existing FAQ (Admin-only).
        """
        pk = kwargs.get('pk')
        try:
            faq = FAQ.objects.get(pk=pk)

            # Exclude updates to the 'question' field
            data = request.data.copy()
          #   data.pop('question', None)

            serializer = FAQSerializer(faq, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return successResponse(data=serializer.data, message="FAQ updated successfully.")
            return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)
        except FAQ.DoesNotExist:
            return errorResponse(message="FAQ not found.", code=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        """
        Delete an FAQ (Admin-only).
        """
        pk = kwargs.get('pk')
        try:
            faq = FAQ.objects.get(pk=pk)
            faq.delete()
            return successResponse(message="FAQ deleted successfully.")
        except FAQ.DoesNotExist:
            return errorResponse(message="FAQ not found.", code=status.HTTP_404_NOT_FOUND)
        
    def patch(self, request, pk=None):
        """
        Toggle the active status of an FAQ (Admin only).
        """
        if not pk:
            return errorResponse(message="FAQ ID is required for toggling status.", code=status.HTTP_400_BAD_REQUEST)
        try:
            faq = FAQ.objects.get(pk=pk)
            faq.is_active = not faq.is_active
            faq.save()
            return successResponse(data={"is_active": faq.is_active}, message="FAQ status updated successfully.")
        except FAQ.DoesNotExist:
            return errorResponse(message="FAQ not found.", code=status.HTTP_404_NOT_FOUND)

# About Us API
class AboutUsView(APIView):
    """
    Single-instance view for About Us content.
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Public access for GET
        return [IsAdminUser()]  # Admin access for POST and PUT

    def get(self, request, *args, **kwargs):
        """
        Retrieve the About Us content.
        """
        about_us = AboutUs.objects.first()
        if not about_us:
            return errorResponse(message="About Us content not found.", code=status.HTTP_404_NOT_FOUND)
        serializer = AboutUsSerializer(about_us)
        return successResponse(data=serializer.data, message="About Us retrieved successfully.")

    def post(self, request, *args, **kwargs):
        """
        Create a new About Us entry.
        Ensures only one entry exists.
        """
        if AboutUs.objects.exists():
            return errorResponse(message="An About Us entry already exists. Please update it instead.", code=status.HTTP_400_BAD_REQUEST)

        serializer = AboutUsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return successResponse(data=serializer.data, message="About Us created successfully.", code=status.HTTP_201_CREATED)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        Update the About Us content.
        """
        about_us = AboutUs.objects.first()
        if not about_us:
            return errorResponse(message="About Us content not found. Create it first.", code=status.HTTP_404_NOT_FOUND)

        serializer = AboutUsSerializer(about_us, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return successResponse(data=serializer.data, message="About Us updated successfully.")
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

# Privacy Policy API
class PrivacyPolicyView(APIView):
    """
    Single-instance view for Privacy Policy content.
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Public access for GET
        return [IsAdminUser()]  # Admin access for POST and PUT

    def get(self, request, *args, **kwargs):
        """
        Retrieve the Privacy Policy content.
        """
        privacy_policy = PrivacyPolicy.objects.first()
        if not privacy_policy:
            return errorResponse(message="Privacy Policy content not found.", code=status.HTTP_404_NOT_FOUND)
        serializer = PrivacyPolicySerializer(privacy_policy)
        return successResponse(data=serializer.data, message="Privacy Policy retrieved successfully.")

    def post(self, request, *args, **kwargs):
        """
        Create a new Privacy Policy entry.
        Ensures only one entry exists.
        """
        if PrivacyPolicy.objects.exists():
            return errorResponse(message="A Privacy Policy entry already exists. Please update it instead.", code=status.HTTP_400_BAD_REQUEST)

        serializer = PrivacyPolicySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return successResponse(data=serializer.data, message="Privacy Policy created successfully.", code=status.HTTP_201_CREATED)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        Update the Privacy Policy content.
        """
        privacy_policy = PrivacyPolicy.objects.first()
        if not privacy_policy:
            return errorResponse(message="Privacy Policy content not found. Create it first.", code=status.HTTP_404_NOT_FOUND)

        serializer = PrivacyPolicySerializer(privacy_policy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return successResponse(data=serializer.data, message="Privacy Policy updated successfully.")
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

# Ask Anything API
class ContactUsView(APIView):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]  # Anyone can create a new message
        return [IsAdminUser()]  # Admin access for all other operations

    def get(self, request, *args, **kwargs):
        """
        Retrieve all messages or a specific message if `pk` is provided.
        """
        pk = kwargs.get('pk')
        if pk:
            try:
                instance = ContactUs.objects.get(pk=pk)
                serializer = self.serializer_class(instance)
                return successResponse(data=serializer.data, message="Message retrieved successfully.")
            except ContactUs.DoesNotExist:
                return errorResponse(message="Message not found.", code=status.HTTP_404_NOT_FOUND)
        else:
            queryset = ContactUs.objects.all()
            serializer = self.serializer_class(queryset, many=True)
            return successResponse(data=serializer.data, message="Messages retrieved successfully.")

    def post(self, request, *args, **kwargs):
        """
        Create a new message.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return successResponse(data=serializer.data, message="Message submitted successfully.", code=status.HTTP_201_CREATED)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None, *args, **kwargs):
          """
          Update the 'reply' field and set 'replied' to True.
          """
          if not pk:
               return errorResponse(message="Message ID is required for updates.", code=status.HTTP_400_BAD_REQUEST)

          try:
               # Fetch the specific message
               message = ContactUs.objects.get(pk=pk)
               
               # Ensure only 'reply' field is updated
               data = {'reply': request.data.get('reply', '')}
               
               serializer = ContactUsSerializer(message, data=data, partial=True)
               if serializer.is_valid():
                    # Save the reply and mark the message as replied
                    serializer.save()
                    message.replied = True
                    message.save()

                    return successResponse(
                         data=serializer.data,
                         message="Reply added successfully and message marked as replied."
                    )
               return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

          except ContactUs.DoesNotExist:
               return errorResponse(message="Message not found.", code=status.HTTP_404_NOT_FOUND)


    def delete(self, request, *args, **kwargs):
        """
        Delete a message (Admin-only).
        """
        pk = kwargs.get('pk')
        try:
            instance = ContactUs.objects.get(pk=pk)
            instance.delete()
            return successResponse(message="Message deleted successfully.")
        except ContactUs.DoesNotExist:
            return errorResponse(message="Message not found.", code=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk=None, *args, **kwargs):
        """
        Toggle the 'replied' status of a specific contact message.
        """
        if not pk:
            return errorResponse(message="Message ID is required.", code=status.HTTP_400_BAD_REQUEST)
        try:
            message = ContactUs.objects.get(pk=pk)
            message.replied = not message.replied
            message.save()
            return successResponse(
                data={"id": message.id, "replied": message.replied},
                message="Message 'replied' status toggled successfully."
            )
        except ContactUs.DoesNotExist:
            return errorResponse(message="Message not found.", code=status.HTTP_404_NOT_FOUND)
        
class SocialMediaView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request, pk=None):
        """
        Get all social media links or filter by active status or get by id.
        """
        if pk:
            # If pk (ID) is provided, return the specific social media link
            try:
                social_media = SocialMedia.objects.get(pk=pk)
            except SocialMedia.DoesNotExist:
                return errorResponse(
                    message="Social media link not found",
                    code=status.HTTP_404_NOT_FOUND
                )

            serializer = SocialMediaSerializer(social_media)
            return successResponse(
                data=serializer.data,
                message="Social media link retrieved successfully",
                code=status.HTTP_200_OK
            )
        
        # Optionally filter by active status
        active = request.query_params.get('is_active', None)
        if active is not None:
            # Convert active parameter to a boolean
            is_active = active.lower() in ['true', '1', 'yes']
            social_media = SocialMedia.objects.filter(is_active=is_active)
        else:
            social_media = SocialMedia.objects.all()

        serializer = SocialMediaSerializer(social_media, many=True)
        return successResponse(
            data=serializer.data,
            message="Social media links retrieved successfully",
            code=status.HTTP_200_OK
        )

    def post(self, request):
        """
        Create a new social media link.
        """
        title = request.data.get('title')
        
        # Check if a social media link with the same title already exists
        if SocialMedia.objects.filter(title=title).exists():
            return errorResponse(
                message="A social media link with this title already exists.",
                code=status.HTTP_400_BAD_REQUEST
            )

        serializer = SocialMediaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save to the database
            return successResponse(
                data=serializer.data,
                message="Social media link added successfully",
                code=status.HTTP_201_CREATED
            )
        return errorResponse(
            message="Error adding social media link",
            details=serializer.errors,
            code=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, pk):
        """
        Update an existing social media link.
        """
        try:
            social_media = SocialMedia.objects.get(pk=pk)
        except SocialMedia.DoesNotExist:
            return errorResponse(
                message="Social media link not found",
                code=status.HTTP_404_NOT_FOUND
            )

        # Check if there is another social media link with the same title (excluding the current one)
        title = request.data.get('title')
        if title and SocialMedia.objects.filter(title=title).exclude(pk=pk).exists():
            return errorResponse(
                message="A social media link with this title already exists.",
                code=status.HTTP_400_BAD_REQUEST
            )

        serializer = SocialMediaSerializer(social_media, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save changes
            return successResponse(
                data=serializer.data,
                message="Social media link updated successfully",
                code=status.HTTP_200_OK
            )
        return errorResponse(
            message="Error updating social media link",
            details=serializer.errors,
            code=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk=None, *args, **kwargs):
        """
        Toggle the is_active status of a social media link.
        """
        try:
            social_media = SocialMedia.objects.get(pk=pk)
            social_media.is_active = not social_media.is_active  # Toggle the is_active status
            social_media.save()

            return successResponse(
                data=SocialMediaSerializer(social_media).data,
                message=f"Social media link {'activated' if social_media.is_active else 'deactivated'} successfully",
                code=status.HTTP_200_OK
            )

        except SocialMedia.DoesNotExist:
            return errorResponse(
                message="Social media link not found",
                code=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        """
        Delete a social media link.
        """
        try:
            social_media = SocialMedia.objects.get(pk=pk)
            social_media.delete()
            return successResponse(
                message="Social media link deleted successfully",
                code=status.HTTP_204_NO_CONTENT
            )
        except SocialMedia.DoesNotExist:
            return errorResponse(
                message="Social media link not found",
                code=status.HTTP_404_NOT_FOUND
            )

# Feedback API
class FeedbackView(APIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request, *args, **kwargs):
        """
        Retrieve all messages or a specific message if `pk` is provided.
        """
        pk = kwargs.get('pk')
        if pk:
            try:
                instance = Feedback.objects.get(pk=pk)
                serializer = self.serializer_class(instance)
                return successResponse(data=serializer.data, message="Message retrieved successfully.")
            except Feedback.DoesNotExist:
                return errorResponse(message="Message not found.", code=status.HTTP_404_NOT_FOUND)
        else:
            queryset = Feedback.objects.all()
            serializer = self.serializer_class(queryset, many=True)
            return successResponse(data=serializer.data, message="Messages retrieved successfully.")

    def post(self, request, *args, **kwargs):
        """
        Create a new message.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return successResponse(data=serializer.data, message="Feedback submitted successfully.", code=status.HTTP_201_CREATED)
        return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None, *args, **kwargs):
          """
          Update the 'reply' field and set 'replied' to True.
          """
          if not pk:
               return errorResponse(message="Message ID is required for updates.", code=status.HTTP_400_BAD_REQUEST)

          try:
               message = Feedback.objects.get(pk=pk)
               
               data = {'reply': request.data.get('reply', '')}
               
               serializer = FeedbackSerializer(message, data=data, partial=True)
               if serializer.is_valid():
                    serializer.save()
                    message.replied = True
                    message.save()

                    return successResponse(
                         data=serializer.data,
                         message="Reply added successfully and message marked as replied."
                    )
               return errorResponse(message="Validation failed", details=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

          except Feedback.DoesNotExist:
               return errorResponse(message="Message not found.", code=status.HTTP_404_NOT_FOUND)


    def delete(self, request, *args, **kwargs):
        """
        Delete a message (Admin-only).
        """
        pk = kwargs.get('pk')
        try:
            instance = Feedback.objects.get(pk=pk)
            instance.delete()
            return successResponse(message="Message deleted successfully.")
        except Feedback.DoesNotExist:
            return errorResponse(message="Message not found.", code=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk=None, *args, **kwargs):
        """
        Toggle the 'replied' status of a specific contact message.
        """
        if not pk:
            return errorResponse(message="Message ID is required.", code=status.HTTP_400_BAD_REQUEST)
        try:
            message = Feedback.objects.get(pk=pk)
            message.replied = not message.replied
            message.save()
            return successResponse(
                data={"id": message.id, "replied": message.replied},
                message="Message 'replied' status toggled successfully."
            )
        except Feedback.DoesNotExist:
            return errorResponse(message="Message not found.", code=status.HTTP_404_NOT_FOUND)

class BlockedUserView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = BlockDetailSerializer

    def get(self, request, *args, **kwargs):
        block_id = kwargs.get('block_id')  # Optional specific block ID

        if block_id:
            # Fetch a specific block by its ID
            try:
                block = Block.objects.get(id=block_id)
                serializer = self.serializer_class(block, context={'request': request})
                return successResponse(data=serializer.data, message="Block detail retrieved successfully.")
            except Block.DoesNotExist:
                return errorResponse(message="Block not found.", code=status.HTTP_404_NOT_FOUND)
        else:
            # Fetch all blocks from the Block table
            blocks = Block.objects.all()
            serializer = self.serializer_class(blocks, many=True, context={'request': request})
            return successResponse(data=serializer.data, message="All block records retrieved successfully.")