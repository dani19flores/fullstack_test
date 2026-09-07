from django.urls import path

from .views import ProductCursorListView, ProductLimitOffsetListView, ProductListView

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path("limit-offset/", ProductLimitOffsetListView.as_view(), name="product-list-limit-offset"),
    path("cursor/", ProductCursorListView.as_view(), name="product-list-cursor"),
]
