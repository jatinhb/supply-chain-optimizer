"""Serializers for orders app."""
from rest_framework import serializers
from django.utils import timezone
from .models import PurchaseOrder, PurchaseOrderItem, OrderHistory


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrderItem model."""

    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    line_total = serializers.ReadOnlyField()
    is_fully_received = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'


class OrderHistorySerializer(serializers.ModelSerializer):
    """Serializer for OrderHistory model."""

    changed_by_name = serializers.CharField(source='changed_by.full_name', read_only=True)

    class Meta:
        model = OrderHistory
        fields = '__all__'


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrder model."""

    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    items_count = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ['order_number', 'total_amount', 'created_by', 'approved_by', 'approved_at']


class PurchaseOrderDetailSerializer(PurchaseOrderSerializer):
    """Detailed serializer with items and history."""

    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    history = OrderHistorySerializer(many=True, read_only=True)


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating purchase orders."""

    items = PurchaseOrderItemSerializer(many=True)

    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'warehouse', 'priority', 'notes', 'expected_delivery', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user

        # Generate order number
        from datetime import datetime
        order_number = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        order = PurchaseOrder.objects.create(
            order_number=order_number,
            created_by=user,
            **validated_data
        )

        for item_data in items_data:
            PurchaseOrderItem.objects.create(order=order, **item_data)

        order.calculate_total()

        # Create initial history
        OrderHistory.objects.create(
            order=order,
            to_status='draft',
            changed_by=user,
            notes='Order created'
        )

        return order


class ApproveOrderSerializer(serializers.Serializer):
    """Serializer for order approval."""

    notes = serializers.CharField(required=False, allow_blank=True)


class ReceiveItemsSerializer(serializers.Serializer):
    """Serializer for receiving order items."""

    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        )
    )
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_items(self, value):
        for item in value:
            if 'item_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError(
                    "Each item must have 'item_id' and 'quantity'"
                )
            if item['quantity'] < 0:
                raise serializers.ValidationError(
                    "Quantity cannot be negative"
                )
        return value
