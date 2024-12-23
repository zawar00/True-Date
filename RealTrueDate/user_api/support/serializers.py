from rest_framework import serializers
from admin_api.support_management.models import FAQ, AboutUs, PrivacyPolicy, ContactUs, SocialMedia, Feedback

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = '__all__'

class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = '__all__'

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['id', 'username', 'email', 'message', 'reply', 'replied']
        read_only_fields = ['id', 'replied', 'reply']

class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = ['id', 'title', 'url', 'icon', 'is_active']
        read_only_fields = ['id', 'is_active']

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'username', 'email', 'description', 'rating', 'reply', 'replied']
        read_only_fields = ['id', 'replied', 'reply']