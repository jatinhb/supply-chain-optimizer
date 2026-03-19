"""Order models for SupplyChainIQ."""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.inventory.models import Product, Supplier, Warehouse


class PurchaseOrder(models.Model):
    """Purchase order model."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('ordered', 'Ordered'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name='purchase_orders'
    )
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.PROTECT, related_name='purchase_orders'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    total_amount = models.DecimalField(
        max_digits=14, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        default=Decimal('0')
    )
    notes = models.TextField(blank=True)
    expected_delivery = models.DateField(null=True, blank=True)
    actual_delivery = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, related_name='created_orders'
    )
    approved_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_orders'
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchase_orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_number} - {self.supplier.name}"

    def calculate_total(self):
        """Recalculate total amount from line items."""
        total = sum(item.line_total for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])
        return total

    @property
    def items_count(self):
        return self.items.count()


class PurchaseOrderItem(models.Model):
    """Line item in a purchase order."""

    order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name='items'
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='order_items'
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_cost = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    received_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'purchase_order_items'
        unique_together = ['order', 'product']

    def __str__(self):
        return f"{self.order.order_number} - {self.product.sku}"

    @property
    def line_total(self):
        return self.quantity * self.unit_cost

    @property
    def is_fully_received(self):
        return self.received_quantity >= self.quantity


class OrderHistory(models.Model):
    """Track purchase order status changes."""

    order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name='history'
    )
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_history'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number}: {self.from_status} -> {self.to_status}"
