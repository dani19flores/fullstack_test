from rest_framework import serializers

from .models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'address_type', 'name', 'nickname',
            'address_line_1', 'address_line_2', 'city',
            'state', 'postal_code', 'country',
        ]
