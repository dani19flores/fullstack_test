from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import RegistrationSerializer


class RegisterAPIView(generics.CreateAPIView):
    """
    Registro de usuarios: valida los datos con RegistrationSerializer,
    crea el User y, en el mismo paso, le genera su token de autenticación
    para que pueda usar la API de inmediato sin pedirlo aparte.
    """
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'token': token.key,
            },
            status=status.HTTP_201_CREATED,
        )
