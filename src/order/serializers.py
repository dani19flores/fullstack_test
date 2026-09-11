from rest_framework import serializers

from products.serializers import ProductSerializer

from .models import Order


class OrderItemSerializer(serializers.Serializer):
    product = ProductSerializer()
    quantity = serializers.IntegerField()


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'status', 'active', 'shipping_total', 'total', 'timestamp', 'items']

    def get_items(self, obj):
        return OrderItemSerializer(obj.cart.items.select_related('product'), many=True).data


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Solo permite cambiar el status: active se recalcula en la vista."""

    class Meta:
        model = Order
        fields = ['status']
