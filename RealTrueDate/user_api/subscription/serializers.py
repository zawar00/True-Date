from rest_framework import serializers
from admin_api.transaction_management.models import SubscriptionPlan, Subscription

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer()  # Nested serializer to show plan details

    class Meta:
        model = Subscription
        fields = '__all__'