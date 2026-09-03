from rest_framework import serializers
from .models import Order, OrderItem
from logistics.models import Shipment

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipment_status = serializers.CharField(source='shipment.status', read_only=True)
    customer_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'status', 'total_price', 'items', 'shipment_status', 
            'shipping_address', 'phone_number', 'customer_email',
            'shipping_delegated', 'created_at', 'updated_at'
        )
