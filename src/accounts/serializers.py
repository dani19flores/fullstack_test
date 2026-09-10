from rest_framework import serializers

from .models import GuestEmail


class GuestEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestEmail
        fields = ['id', 'email']
