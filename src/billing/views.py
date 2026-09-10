from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import BillingProfile
from .serializers import BillingProfileSerializer


class MyBillingProfileAPIView(generics.RetrieveAPIView):
    """
    Perfil de facturación del usuario autenticado. Se crea solo, vía
    señal, en el momento en que se registra (ver billing/models.py).
    """
    serializer_class = BillingProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(BillingProfile, user=self.request.user)
