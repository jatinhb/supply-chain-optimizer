"""Analytics models for SupplyChainIQ."""
from django.db import models


class DashboardMetrics(models.Model):
    """Store daily dashboard metrics snapshot."""

    date = models.DateField(unique=True)
    total_products = models.PositiveIntegerField(default=0)
    total_warehouses = models.PositiveIntegerField(default=0)
    total_inventory_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    inventory_turnover_rate = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    stockout_rate = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    fill_rate = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    average_lead_time = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    pending_orders = models.PositiveIntegerField(default=0)
    low_stock_items = models.PositiveIntegerField(default=0)
    out_of_stock_items = models.PositiveIntegerField(default=0)
    forecast_accuracy = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dashboard_metrics'
        ordering = ['-date']

    def __str__(self):
        return f"Metrics for {self.date}"


class SupplierPerformance(models.Model):
    """Track supplier performance metrics."""

    supplier = models.ForeignKey(
        'inventory.Supplier', on_delete=models.CASCADE,
        related_name='performance_records'
    )
    period_start = models.DateField()
    period_end = models.DateField()
    total_orders = models.PositiveIntegerField(default=0)
    on_time_deliveries = models.PositiveIntegerField(default=0)
    late_deliveries = models.PositiveIntegerField(default=0)
    quality_issues = models.PositiveIntegerField(default=0)
    average_lead_time = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    on_time_rate = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    quality_rate = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'supplier_performance'
        ordering = ['-period_end']

    def __str__(self):
        return f"{self.supplier.name} - {self.period_start} to {self.period_end}"


class CategoryAnalytics(models.Model):
    """Analytics per product category."""

    category = models.ForeignKey(
        'inventory.Category', on_delete=models.CASCADE,
        related_name='analytics'
    )
    date = models.DateField()
    total_products = models.PositiveIntegerField(default=0)
    total_stock = models.PositiveIntegerField(default=0)
    total_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    average_turnover = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    stockout_count = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    profit_margin = models.DecimalField(max_digits=8, decimal_places=4, default=0)

    class Meta:
        db_table = 'category_analytics'
        unique_together = ['category', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.category.name} - {self.date}"


class CostAnalysis(models.Model):
    """Track supply chain costs."""

    COST_TYPES = [
        ('holding', 'Holding Cost'),
        ('ordering', 'Ordering Cost'),
        ('stockout', 'Stockout Cost'),
        ('transport', 'Transportation Cost'),
        ('handling', 'Handling Cost'),
    ]

    cost_type = models.CharField(max_length=20, choices=COST_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    warehouse = models.ForeignKey(
        'inventory.Warehouse', on_delete=models.CASCADE,
        null=True, blank=True, related_name='cost_analyses'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cost_analysis'
        ordering = ['-period_end']

    def __str__(self):
        return f"{self.get_cost_type_display()} - {self.period_start} to {self.period_end}"
