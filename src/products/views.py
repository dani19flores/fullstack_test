from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Product
from .serializers import ProductSerializer
from .pagination import ProductCPagination, ProductLDPagionation, ProductPagination


class ProductListView(generics.ListAPIView):
    """PageNumberPagination: ?p=<pagina>&size=<tamaño>"""
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    pagination_class = ProductPagination


class ProductLimitOffsetListView(generics.ListAPIView):
    """LimitOffsetPagination: ?records=<limite>&start=<offset>"""
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    pagination_class = ProductLDPagionation


class ProductCursorListView(generics.ListAPIView):
    """CursorPagination: ?cur=<cursor>"""
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    pagination_class = ProductCPagination
    permiission_classes = [IsAuthenticated]
