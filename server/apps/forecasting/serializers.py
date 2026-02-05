"""Serializers for forecasting app."""
from rest_framework import serializers
from .models import DemandHistory, DemandForecast, ForecastAccuracy, SeasonalityPattern


class DemandHistorySerializer(serializers.ModelSerializer):
    """Serializer for DemandHistory model."""

    product_sku = serializers.CharField(source='product.sku', read_only=True)

    class Meta:
        model = DemandHistory
        fields = '__all__'


class DemandForecastSerializer(serializers.ModelSerializer):
    """Serializer for DemandForecast model."""

    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = DemandForecast
        fields = '__all__'


class ForecastAccuracySerializer(serializers.ModelSerializer):
    """Serializer for ForecastAccuracy model."""

    product_sku = serializers.CharField(source='product.sku', read_only=True)

    class Meta:
        model = ForecastAccuracy
        fields = '__all__'


class SeasonalityPatternSerializer(serializers.ModelSerializer):
    """Serializer for SeasonalityPattern model."""

    class Meta:
        model = SeasonalityPattern
        fields = '__all__'


class ForecastRequestSerializer(serializers.Serializer):
    """Serializer for forecast generation request."""

    product_id = serializers.IntegerField()
    horizon_weeks = serializers.IntegerField(min_value=1, max_value=52, default=12)
    model_type = serializers.ChoiceField(
        choices=['prophet', 'xgboost', 'ensemble', 'arima'],
        default='prophet'
    )
    confidence_level = serializers.DecimalField(
        max_digits=5, decimal_places=2,
        min_value=80, max_value=99.9,
        default=95.0
    )


class ForecastResultSerializer(serializers.Serializer):
    """Serializer for forecast results."""

    product_id = serializers.IntegerField()
    product_sku = serializers.CharField()
    product_name = serializers.CharField()
    model_type = serializers.CharField()
    accuracy = serializers.FloatField()
    trend = serializers.CharField()
    total_forecasted_demand = serializers.FloatField()
    peak_demand_date = serializers.DateField()
    peak_demand_value = serializers.FloatField()
    suggested_safety_stock = serializers.IntegerField()
    suggested_reorder_quantity = serializers.IntegerField()
    forecasts = DemandForecastSerializer(many=True)


class BulkForecastRequestSerializer(serializers.Serializer):
    """Serializer for bulk forecast generation."""

    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text='List of product IDs. If empty, forecasts all active products.'
    )
    horizon_weeks = serializers.IntegerField(min_value=1, max_value=52, default=12)
    model_type = serializers.ChoiceField(
        choices=['prophet', 'xgboost', 'ensemble'],
        default='prophet'
    )
