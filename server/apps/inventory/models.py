"""Inventory models for SupplyChainIQ."""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Supplier(models.Model):
    """Supplier model."""

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    contact_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    lead_time_days = models.PositiveIntegerField(default=7)
    reliability_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        default=Decimal('100.00')
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'suppliers'
        ordering = ['name']

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    """Warehouse model."""

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(help_text='Total storage capacity in units')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'warehouses'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def current_utilization(self):
        """Calculate current warehouse utilization percentage."""
        total_stock = self.inventory_items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        return round((total_stock / self.capacity) * 100, 2) if self.capacity > 0 else 0


class Category(models.Model):
    """Product category model."""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='children'
    )

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model."""

    ABC_CHOICES = [
        ('A', 'A - High Value'),
        ('B', 'B - Medium Value'),
        ('C', 'C - Low Value'),
    ]

    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='products'
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name='products'
    )
    unit_cost = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    lead_time_days = models.PositiveIntegerField(default=7)
    reorder_point = models.PositiveIntegerField(default=100)
    safety_stock = models.PositiveIntegerField(default=50)
    economic_order_quantity = models.PositiveIntegerField(null=True, blank=True)
    abc_class = models.CharField(max_length=1, choices=ABC_CHOICES, default='C')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['sku']

    def __str__(self):
        return f"{self.sku} - {self.name}"

    @property
    def profit_margin(self):
        """Calculate profit margin percentage."""
        if self.unit_price > 0:
            return round(((self.unit_price - self.unit_cost) / self.unit_price) * 100, 2)
        return 0


class InventoryItem(models.Model):
    """Inventory item tracking stock levels per warehouse."""

    STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('reserved', 'Reserved'),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='inventory_items'
    )
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name='inventory_items'
    )
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    min_quantity = models.PositiveIntegerField(default=0)
    max_quantity = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=50, blank=True, help_text='Bin/shelf location')
    last_counted = models.DateTimeField(null=True, blank=True)
    last_restocked = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'inventory_items'
        unique_together = ['product', 'warehouse']
        ordering = ['product__sku']

    def __str__(self):
        return f"{self.product.sku} @ {self.warehouse.code}"

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity

    @property
    def status(self):
        if self.quantity == 0:
            return 'out_of_stock'
        if self.quantity <= self.product.reorder_point:
            return 'low_stock'
        return 'in_stock'

    @property
    def total_value(self):
        return self.quantity * self.product.unit_cost

    @property
    def days_of_stock(self):
        """Estimate days of stock based on average daily demand."""
        # This would typically come from forecasting service
        avg_daily_demand = 10  # Placeholder
        return self.quantity // avg_daily_demand if avg_daily_demand > 0 else 999


class StockMovement(models.Model):
    """Track stock movements (in/out)."""

    MOVEMENT_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('transfer', 'Transfer'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
    ]

    inventory_item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE, related_name='movements'
    )
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()  # Can be negative for stock out
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stock_movements'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.movement_type}: {self.quantity} units"
