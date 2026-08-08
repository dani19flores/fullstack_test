from django.urls import path

from analytics import views

urlpatterns = [
    path("sales", views.SalesView.as_view(), name="sales-analytics"),
    path("sales/data", views.SalesAjaxView.as_view(), name="sales-data"),
]
