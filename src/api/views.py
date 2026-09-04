from rest_framework import viewsets, views
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo sobre Product: expone create, list, retrieve,
    update, partial_update y destroy usando la base de datos real.
    """
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer


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
