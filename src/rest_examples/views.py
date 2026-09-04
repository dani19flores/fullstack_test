from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import TestSerializer
from rest_framework import status


class TestAPIView(APIView):
    """A simple API view that returns a greeting message.
    """
    serializer_class = TestSerializer

    def get(self, request, format=None):
        """Regresa una lista de caracteres de un APIView."""
        apiView_info = [
            "Usa método HTTP como funciones (get, post, patch, put, delete)",
            "Es similar a un Django View tradiccional",
            "Te d e el mayor control de la lógica de tu aplicación",
            "Es mapeado manualmente a URLs usando un archivo urls.py",
        ]
        return Response({"message": "Hola!", "apiView_info": apiView_info})

    def post(self, request):
        """Crea un mensaje de saludo personalizado."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get("name")
            return Response({"message": f"Hola {name}!"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        """Actualiza un mensaje de saludo personalizado."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get("name")
            return Response({"message": f"Hola {name}! (actualizado)"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        """Actualiza parcialmente un mensaje de saludo personalizado."""
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            name = serializer.validated_data.get("name")
            return Response({"message": f"Hola {name}! (parcialmente actualizado)"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        """Elimina un mensaje de saludo personalizado."""
        return Response({"message": "Mensaje eliminado!"}, status=status.HTTP_204_NO_CONTENT)