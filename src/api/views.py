from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, views
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ViewSet):
    """
    ViewSet sobre Product con cada método de CRUD implementado de forma
    explícita: create, list, retrieve, update, partial_update y destroy.
    """
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer

    def list(self, request):
        """list – Listar todos los productos."""
        products = self.queryset
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data)

    def create(self, request):
        """create – Crear un producto nuevo."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """retrieve – Consultar un producto puntual por su id."""
        product = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(product)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """update – Actualizar todos los campos de un producto."""
        product = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """partial_update – Actualizar solo algunos campos de un producto."""
        product = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """destroy – Borrar un producto."""
        product = get_object_or_404(self.queryset, pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductAPIView(views.APIView):

    def get(self, request, *args, **kwargs):
        content = {
            "detail": "Estás en método GET de la vista ProductAPIView"
        }
        return Response(content)

    def post(self, request, *args, **kwargs):
        content = {
            "detail": "Estás en método POST de la vista ProductAPIView"
        }
        return Response(content)

    def put(self, request, *args, **kwargs):
        content = {
            "detail": "Estás en método PUT de la vista ProductAPIView"
        }
        return Response(content)

    def delete(self, request, *args, **kwargs):
        content = {
            "detail": "Estás en método DELETE de la vista ProductAPIView"
        }
        return Response(content)
