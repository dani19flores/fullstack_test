from rest_framework import serializers

class TestSerializer(serializers.Serializer):
    """A simple serializer that defines the fields for a test API."""
    name = serializers.CharField(max_length=100)