from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ProductAPIView, ProductViewSet

router = SimpleRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path("", ProductAPIView.as_view(), name="product-list"),
    path("", include(router.urls)),
]
