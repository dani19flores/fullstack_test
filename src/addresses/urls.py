from django.urls import path

from .views import AddressListCreateAPIView

urlpatterns = [
    path('', AddressListCreateAPIView.as_view(), name='my-addresses'),
]
