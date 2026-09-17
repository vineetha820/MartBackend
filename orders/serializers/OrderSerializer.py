from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from Products.models import Product
from orders.models import Order, OrderItem


class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'unit_price', 'subtotal')
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'user',
            'status',
            'recipient_name',
            'phone',
            'shipping_address',
            'total_amount',
            'items',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class OrderCreateSerializer(serializers.ModelSerializer):
        items = OrderItemCreateSerializer(many=True, allow_empty=False, write_only=True)

        class Meta:
            model = Order
            fields = (
                'id',
                'recipient_name',
                'phone',
                'shipping_address',
                'items',
                'total_amount',
            )
            read_only_fields = ('id', 'total_amount')

        @transaction.atomic
        def create(self, validated_data):
            items_data = validated_data.pop('items')
            user = validated_data.pop('user')

            total_amount = sum(
                (item['product'].price * item['quantity'] for item in items_data),
                Decimal('0.00'),
            )

            order = Order.objects.create(
                user=user,
                total_amount=total_amount,
                **validated_data,
            )

            for item in items_data:
                product = item['product']
                quantity = item['quantity']
                subtotal = product.price * quantity

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    quantity=quantity,
                    unit_price=product.price,
                    subtotal=subtotal,
                )

            return order
