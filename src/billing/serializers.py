from rest_framework import serializers

from .models import BillingProfile


class BillingProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingProfile
        fields = ['id', 'email', 'active', 'customer_id', 'timestamp']
        read_only_fields = fields
