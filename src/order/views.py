from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from billing.models import BillingProfile
from carts.models import Cart, CartItem
from products.models import Product

from .models import Order
from .serializers import OrderSerializer, OrderStatusUpdateSerializer

SHIPPING_TOTAL = Decimal("5.99")


class CheckoutAPIView(views.APIView):
    """
    Crea una orden real a partir del carrito que manda el frontend:
    body = {"items": [{"product_id": 1, "quantity": 2}, ...]}.
    Crea el Cart/CartItem del usuario y la Order sobre esos datos —
    nunca confía en el total que mande el cliente, lo recalcula del
    precio real de cada producto.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        items_payload = request.data.get('items', [])
        if not items_payload:
            return Response({"detail": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        billing_profile, _ = BillingProfile.objects.get_or_create(
            user=request.user, defaults={"email": request.user.email}
        )

        cart = Cart.objects.create(user=request.user)
        subtotal = Decimal("0.00")
        for entry in items_payload:
            product = get_object_or_404(Product, pk=entry.get('product_id'))
            quantity = max(int(entry.get('quantity', 1)), 1)
            CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            subtotal += product.price * quantity
        cart.subtotal = subtotal
        cart.total = subtotal
        cart.save()

        order = Order.objects.create(
            billing_profile=billing_profile,
            cart=cart,
            shipping_total=SHIPPING_TOTAL,
            total=subtotal + SHIPPING_TOTAL,
        )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderListAPIView(generics.ListAPIView):
    """Órdenes del usuario autenticado, más recientes primero."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(billing_profile__user=self.request.user)


class OrderDetailAPIView(views.APIView):
    """
    Detalle/actualización de una orden propia. PATCH/PUT solo aceptan
    status; si el nuevo status es 'canceled' o 'refunded' la orden
    también se marca active=False, para que el conteo de "activas" no
    dependa de que el cliente mande ese campo aparte.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(Order, pk=pk, billing_profile__user=request.user)

    def get(self, request, pk, *args, **kwargs):
        order = self.get_object(request, pk)
        return Response(OrderSerializer(order).data)

    def patch(self, request, pk, *args, **kwargs):
        order = self.get_object(request, pk)
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        if order.status in ('canceled', 'refunded'):
            order.active = False
            order.save(update_fields=['active'])
        return Response(OrderSerializer(order).data)

    def put(self, request, pk, *args, **kwargs):
        return self.patch(request, pk, *args, **kwargs)
