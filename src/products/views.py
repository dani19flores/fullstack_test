from rest_framework import generics

from .models import Product
from .serializers import ProductSerializer
from .pagination import ProductCPagination, ProductPagination


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductCPagination
