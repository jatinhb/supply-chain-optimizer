"""Celery tasks for inventory app."""
from celery import shared_task
from django.db.models import F
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def check_reorder_points():
    """Check inventory levels and create alerts for items below reorder point."""
    from .models import InventoryItem

    low_stock_items = InventoryItem.objects.filter(
        quantity__lte=F('product__reorder_point')
    ).select_related('product', 'warehouse')

    alerts_created = 0
    for item in low_stock_items:
        # Here you would create alerts in your alert system
        # For now, we'll just count them
        alerts_created += 1

    return f"Checked inventory levels. Found {alerts_created} items below reorder point."


@shared_task
def update_abc_classification():
    """Update ABC classification for all products based on sales value."""
    from .models import Product
    from django.db.models import Sum

    # Get total value for each product
    products = Product.objects.annotate(
        total_value=Sum('inventory_items__quantity') * F('unit_cost')
    ).order_by('-total_value')

    total_products = products.count()
    if total_products == 0:
        return "No products to classify"

    # A = top 20% by value, B = next 30%, C = remaining 50%
    a_threshold = int(total_products * 0.2)
    b_threshold = int(total_products * 0.5)

    updates = {'A': 0, 'B': 0, 'C': 0}

    for i, product in enumerate(products):
        if i < a_threshold:
            new_class = 'A'
        elif i < b_threshold:
            new_class = 'B'
        else:
            new_class = 'C'

        if product.abc_class != new_class:
            product.abc_class = new_class
            product.save(update_fields=['abc_class'])
            updates[new_class] += 1

    return f"ABC classification updated: A={updates['A']}, B={updates['B']}, C={updates['C']}"


@shared_task
def generate_inventory_report():
    """Generate daily inventory report."""
    from .models import InventoryItem, Product
    from django.db.models import Sum

    # Aggregate statistics
    stats = InventoryItem.objects.aggregate(
        total_items=Sum('quantity'),
        total_reserved=Sum('reserved_quantity'),
    )

    total_value = sum(
        item.total_value for item in InventoryItem.objects.select_related('product')
    )

    out_of_stock = InventoryItem.objects.filter(quantity=0).count()
    low_stock = InventoryItem.objects.filter(
        quantity__gt=0,
        quantity__lte=F('product__reorder_point')
    ).count()

    report = {
        'total_items': stats['total_items'] or 0,
        'total_reserved': stats['total_reserved'] or 0,
        'total_value': float(total_value),
        'out_of_stock_count': out_of_stock,
        'low_stock_count': low_stock,
        'total_products': Product.objects.filter(is_active=True).count(),
    }

    return report
