from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import TestAPIView, TestViewSet

router = DefaultRouter()
router.register("test-viewset", TestViewSet, basename="test-viewset")

urlpatterns = [
    path("", TestAPIView.as_view(), name="test_api_view"),
    path("", include(router.urls)),
]