from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'user', 'title', 'slug', 'price']


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Valida los datos de un usuario nuevo (username único, email con formato
    válido, password con un mínimo de longitud) y sabe crear el User con la
    contraseña bien hasheada — nunca la guarda en texto plano.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
