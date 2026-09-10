from django.urls import path

from .views import GuestEmailCreateAPIView

urlpatterns = [
    path('', GuestEmailCreateAPIView.as_view(), name='guest-email'),
]
