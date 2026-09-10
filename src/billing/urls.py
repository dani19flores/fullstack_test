from django.urls import path

from .views import MyBillingProfileAPIView

urlpatterns = [
    path('mine/', MyBillingProfileAPIView.as_view(), name='my-billing-profile'),
]
