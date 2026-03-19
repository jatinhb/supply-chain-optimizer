"""Forecasting models for SupplyChainIQ."""
from django.db import models
from apps.inventory.models import Product


class DemandHistory(models.Model):
    """Historical demand data for forecasting."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='demand_history'
    )
    date = models.DateField()
    quantity = models.PositiveIntegerField()
    # External factors that may affect demand
    is_promotion = models.BooleanField(default=False)
    is_holiday = models.BooleanField(default=False)
    price_at_time = models.DecimalField(max_digits=12, decimal_places=2, null=True)

    class Meta:
        db_table = 'demand_history'
        unique_together = ['product', 'date']
        ordering = ['product', '-date']
        indexes = [
            models.Index(fields=['product', 'date']),
        ]

    def __str__(self):
        return f"{self.product.sku} - {self.date}: {self.quantity}"


class DemandForecast(models.Model):
    """Demand forecast predictions."""

    MODEL_TYPES = [
        ('prophet', 'Prophet'),
        ('xgboost', 'XGBoost'),
        ('ensemble', 'Ensemble'),
        ('arima', 'ARIMA'),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='forecasts'
    )
    forecast_date = models.DateField(help_text='Date being forecasted')
    predicted_demand = models.DecimalField(max_digits=12, decimal_places=2)
    lower_bound = models.DecimalField(max_digits=12, decimal_places=2)
    upper_bound = models.DecimalField(max_digits=12, decimal_places=2)
    confidence_level = models.DecimalField(
        max_digits=5, decimal_places=2, default=95.0
    )
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'demand_forecasts'
        unique_together = ['product', 'forecast_date', 'model_type']
        ordering = ['product', 'forecast_date']
        indexes = [
            models.Index(fields=['product', 'forecast_date']),
        ]

    def __str__(self):
        return f"{self.product.sku} - {self.forecast_date}: {self.predicted_demand}"


class ForecastAccuracy(models.Model):
    """Track forecast accuracy metrics."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='forecast_accuracy'
    )
    model_type = models.CharField(max_length=20, choices=DemandForecast.MODEL_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()
    mape = models.DecimalField(
        max_digits=8, decimal_places=4,
        help_text='Mean Absolute Percentage Error'
    )
    rmse = models.DecimalField(
        max_digits=12, decimal_places=4,
        help_text='Root Mean Square Error'
    )
    mae = models.DecimalField(
        max_digits=12, decimal_places=4,
        help_text='Mean Absolute Error'
    )
    r_squared = models.DecimalField(
        max_digits=8, decimal_places=6,
        help_text='R-squared coefficient'
    )
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'forecast_accuracy'
        ordering = ['-calculated_at']

    def __str__(self):
        return f"{self.product.sku} - {self.model_type}: MAPE={self.mape}%"


class SeasonalityPattern(models.Model):
    """Store detected seasonality patterns."""

    PATTERN_TYPES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='seasonality_patterns'
    )
    pattern_type = models.CharField(max_length=20, choices=PATTERN_TYPES)
    period_index = models.PositiveIntegerField(
        help_text='1-7 for weekly, 1-12 for monthly, etc.'
    )
    factor = models.DecimalField(
        max_digits=8, decimal_places=6,
        help_text='Multiplicative factor (1.0 = no effect)'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'seasonality_patterns'
        unique_together = ['product', 'pattern_type', 'period_index']
        ordering = ['product', 'pattern_type', 'period_index']

    def __str__(self):
        return f"{self.product.sku} - {self.pattern_type} [{self.period_index}]: {self.factor}"
