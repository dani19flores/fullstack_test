from rest_framework import generics, status, views
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import RegistrationSerializer


class RegisterAPIView(generics.CreateAPIView):
    """
    Registro de usuarios: valida los datos con RegistrationSerializer,
    crea el User (el token se genera solo vía la señal post_save en
    models.py) y devuelve ambos en la respuesta.
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


class LogoutAPIView(views.APIView):
    """Cierra la sesión de API: borra el token del usuario autenticado."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
