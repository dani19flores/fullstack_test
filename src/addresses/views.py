from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from billing.models import BillingProfile

from .models import Address
from .serializers import AddressSerializer


class AddressListCreateAPIView(generics.ListCreateAPIView):
    """
    Lista y crea direcciones del usuario autenticado. billing_profile
    nunca se toma del cliente: siempre se usa el del usuario logueado,
    así nadie puede crear/ver direcciones de otra cuenta.
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(billing_profile__user=self.request.user)

    def perform_create(self, serializer):
        billing_profile = BillingProfile.objects.get(user=self.request.user)
        serializer.save(billing_profile=billing_profile)
