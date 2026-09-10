from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import GuestEmail
from .serializers import GuestEmailSerializer


class GuestEmailCreateAPIView(generics.CreateAPIView):
    """
    Captura el correo de un visitante sin cuenta (newsletter / checkout
    de invitado). Público a propósito: no tiene sentido pedir login
    para algo pensado justo para quien todavía no se registra.
    """
    queryset = GuestEmail.objects.all()
    serializer_class = GuestEmailSerializer
    permission_classes = [AllowAny]
