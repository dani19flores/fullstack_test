from django.urls import path

from ventas import views

app_name = 'ventas'

urlpatterns = [
    path('', views.product_list, name='product-list'),
    path('agregar/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('pedido/', views.process_order, name='process-order'),
]
