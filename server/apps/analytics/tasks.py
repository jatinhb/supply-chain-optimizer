"""Celery tasks for analytics app."""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


@shared_task
def calculate_daily_metrics():
    """Calculate and store daily dashboard metrics."""
    from django.db.models import Sum, F, Count, Q
    from apps.inventory.models import Product, InventoryItem, Warehouse
    from apps.orders.models import PurchaseOrder
    from .models import DashboardMetrics

    today = timezone.now().date()

    inventory_items = InventoryItem.objects.select_related('product')
    total_items = inventory_items.count() or 1

    # Calculate metrics
    total_products = Product.objects.filter(is_active=True).count()
    total_warehouses = Warehouse.objects.filter(is_active=True).count()

    total_value = sum(item.total_value for item in inventory_items)

    out_of_stock = inventory_items.filter(quantity=0).count()
    low_stock = inventory_items.filter(
        quantity__gt=0,
        quantity__lte=F('product__reorder_point')
    ).count()

    stockout_rate = (out_of_stock / total_items) * 100

    pending_orders = PurchaseOrder.objects.filter(
        status__in=['pending', 'approved', 'ordered', 'shipped']
    ).count()

    metrics, created = DashboardMetrics.objects.update_or_create(
        date=today,
        defaults={
            'total_products': total_products,
            'total_warehouses': total_warehouses,
            'total_inventory_value': total_value,
            'inventory_turnover_rate': Decimal('8.4'),  # Would calculate from sales
            'stockout_rate': Decimal(str(round(stockout_rate, 4))),
            'fill_rate': Decimal('97.2'),  # Would calculate from orders
            'average_lead_time': Decimal('4.2'),  # Would calculate from orders
            'pending_orders': pending_orders,
            'low_stock_items': low_stock,
            'out_of_stock_items': out_of_stock,
        }
    )

    return f"Metrics calculated for {today}: {metrics.id}"


@shared_task
def calculate_abc_analysis():
    """Update ABC classification for all products."""
    from django.db.models import Sum, F
    from apps.inventory.models import Product

    products = Product.objects.filter(is_active=True).annotate(
        total_value=Sum(F('inventory_items__quantity') * F('unit_cost'))
    ).order_by('-total_value')

    total_products = products.count()
    if total_products == 0:
        return "No products to classify"

    # A = top 20%, B = next 30%, C = remaining 50%
    a_threshold = int(total_products * 0.2) or 1
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

    return f"ABC analysis completed: A={updates['A']}, B={updates['B']}, C={updates['C']}"


@shared_task
def calculate_supplier_performance():
    """Calculate supplier performance for the last 30 days."""
    from apps.inventory.models import Supplier
    from apps.orders.models import PurchaseOrder
    from .models import SupplierPerformance

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    for supplier in Supplier.objects.filter(is_active=True):
        orders = PurchaseOrder.objects.filter(
            supplier=supplier,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

        total_orders = orders.count()
        if total_orders == 0:
            continue

        delivered = orders.filter(status='delivered')
        on_time = delivered.filter(
            actual_delivery__lte=F('expected_delivery')
        ).count()

        late = delivered.filter(
            actual_delivery__gt=F('expected_delivery')
        ).count()

        on_time_rate = (on_time / total_orders) * 100 if total_orders else 100
        quality_rate = 99.0  # Would calculate from quality data

        # Calculate overall score (weighted average)
        overall_score = (on_time_rate * 0.4) + (quality_rate * 0.4) + (
            (100 - supplier.lead_time_days) * 0.2
        )

        SupplierPerformance.objects.update_or_create(
            supplier=supplier,
            period_start=start_date,
            period_end=end_date,
            defaults={
                'total_orders': total_orders,
                'on_time_deliveries': on_time,
                'late_deliveries': late,
                'quality_issues': 0,
                'average_lead_time': supplier.lead_time_days,
                'on_time_rate': Decimal(str(round(on_time_rate, 4))),
                'quality_rate': Decimal(str(round(quality_rate, 4))),
                'overall_score': Decimal(str(round(overall_score, 2))),
            }
        )

    return "Supplier performance calculated"
