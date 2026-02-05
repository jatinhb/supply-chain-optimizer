"""Serializers for inventory app."""
from rest_framework import serializers
from .models import Supplier, Warehouse, Category, Product, InventoryItem, StockMovement


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier model."""

    class Meta:
        model = Supplier
        fields = '__all__'


class WarehouseSerializer(serializers.ModelSerializer):
    """Serializer for Warehouse model."""

    current_utilization = serializers.ReadOnlyField()

    class Meta:
        model = Warehouse
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""

    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""

    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    profit_margin = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product lists."""

    class Meta:
        model = Product
        fields = ['id', 'sku', 'name', 'category', 'unit_cost', 'unit_price', 'abc_class']


class InventoryItemSerializer(serializers.ModelSerializer):
    """Serializer for InventoryItem model."""

    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    status = serializers.ReadOnlyField()
    available_quantity = serializers.ReadOnlyField()
    total_value = serializers.ReadOnlyField()
    days_of_stock = serializers.ReadOnlyField()

    class Meta:
        model = InventoryItem
        fields = '__all__'


class InventoryItemDetailSerializer(InventoryItemSerializer):
    """Detailed serializer with recent movements."""

    recent_movements = serializers.SerializerMethodField()

    def get_recent_movements(self, obj):
        movements = obj.movements.all()[:10]
        return StockMovementSerializer(movements, many=True).data


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for StockMovement model."""

    created_by_name = serializers.CharField(
        source='created_by.full_name', read_only=True
    )

    class Meta:
        model = StockMovement
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']


class StockAdjustmentSerializer(serializers.Serializer):
    """Serializer for stock adjustments."""

    quantity = serializers.IntegerField()
    movement_type = serializers.ChoiceField(
        choices=['in', 'out', 'adjustment', 'return']
    )
    reference = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class ReorderAlertSerializer(serializers.Serializer):
    """Serializer for reorder alerts."""

    product_id = serializers.IntegerField()
    sku = serializers.CharField()
    product_name = serializers.CharField()
    current_stock = serializers.IntegerField()
    reorder_point = serializers.IntegerField()
    suggested_quantity = serializers.IntegerField()
    estimated_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    priority = serializers.CharField()
    warehouse = serializers.CharField()
