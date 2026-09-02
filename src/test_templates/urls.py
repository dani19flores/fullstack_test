from django.urls import path

from .views import detail_view, test_view

urlpatterns = [
    path("", test_view, name="test-view"),
    path("detail/", detail_view, name="detail-view"),
]