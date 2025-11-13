"""Admin configuration for analytics app."""
from django.contrib import admin
from .models import DashboardMetrics, SupplierPerformance, CategoryAnalytics, CostAnalysis


@admin.register(DashboardMetrics)
class DashboardMetricsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_products', 'total_inventory_value', 'stockout_rate', 'forecast_accuracy']
    date_hierarchy = 'date'


@admin.register(SupplierPerformance)
class SupplierPerformanceAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'period_start', 'period_end', 'on_time_rate', 'quality_rate', 'overall_score']
    list_filter = ['supplier']


@admin.register(CategoryAnalytics)
class CategoryAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['category', 'date', 'total_products', 'total_value', 'stockout_count']
    list_filter = ['category']
    date_hierarchy = 'date'


@admin.register(CostAnalysis)
class CostAnalysisAdmin(admin.ModelAdmin):
    list_display = ['cost_type', 'period_start', 'period_end', 'amount', 'warehouse']
    list_filter = ['cost_type', 'warehouse']
