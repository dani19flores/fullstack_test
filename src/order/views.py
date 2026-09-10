from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from billing.models import BillingProfile
from carts.models import Cart, CartItem
from products.models import Product

from .models import Order
from .serializers import OrderSerializer

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
