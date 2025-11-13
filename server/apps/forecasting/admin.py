"""Admin configuration for forecasting app."""
from django.contrib import admin
from .models import DemandHistory, DemandForecast, ForecastAccuracy, SeasonalityPattern


@admin.register(DemandHistory)
class DemandHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'date', 'quantity', 'is_promotion', 'is_holiday']
    list_filter = ['is_promotion', 'is_holiday', 'date']
    search_fields = ['product__sku', 'product__name']
    date_hierarchy = 'date'


@admin.register(DemandForecast)
class DemandForecastAdmin(admin.ModelAdmin):
    list_display = ['product', 'forecast_date', 'predicted_demand', 'model_type', 'created_at']
    list_filter = ['model_type', 'forecast_date']
    search_fields = ['product__sku', 'product__name']
    date_hierarchy = 'forecast_date'


@admin.register(ForecastAccuracy)
class ForecastAccuracyAdmin(admin.ModelAdmin):
    list_display = ['product', 'model_type', 'mape', 'rmse', 'r_squared', 'calculated_at']
    list_filter = ['model_type', 'calculated_at']
    search_fields = ['product__sku']


@admin.register(SeasonalityPattern)
class SeasonalityPatternAdmin(admin.ModelAdmin):
    list_display = ['product', 'pattern_type', 'period_index', 'factor']
    list_filter = ['pattern_type']
    search_fields = ['product__sku']
