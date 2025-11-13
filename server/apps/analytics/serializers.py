"""Serializers for analytics app."""
from rest_framework import serializers
from .models import DashboardMetrics, SupplierPerformance, CategoryAnalytics, CostAnalysis


class DashboardMetricsSerializer(serializers.ModelSerializer):
    """Serializer for DashboardMetrics model."""

    class Meta:
        model = DashboardMetrics
        fields = '__all__'


class SupplierPerformanceSerializer(serializers.ModelSerializer):
    """Serializer for SupplierPerformance model."""

    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = SupplierPerformance
        fields = '__all__'


class CategoryAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for CategoryAnalytics model."""

    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = CategoryAnalytics
        fields = '__all__'


class CostAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for CostAnalysis model."""

    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    cost_type_display = serializers.CharField(source='get_cost_type_display', read_only=True)

    class Meta:
        model = CostAnalysis
        fields = '__all__'


class ABCAnalysisSerializer(serializers.Serializer):
    """Serializer for ABC analysis results."""

    class_name = serializers.CharField()
    product_count = serializers.IntegerField()
    percentage = serializers.FloatField()
    total_value = serializers.DecimalField(max_digits=14, decimal_places=2)
    value_percentage = serializers.FloatField()


class InventoryKPISerializer(serializers.Serializer):
    """Serializer for inventory KPIs."""

    inventory_turnover = serializers.FloatField()
    fill_rate = serializers.FloatField()
    stockout_rate = serializers.FloatField()
    average_inventory_value = serializers.DecimalField(max_digits=14, decimal_places=2)
    carrying_cost = serializers.DecimalField(max_digits=14, decimal_places=2)
    order_accuracy = serializers.FloatField()
