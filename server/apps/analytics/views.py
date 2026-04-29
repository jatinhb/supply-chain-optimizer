"""Views for analytics app."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Avg, F, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.inventory.models import Product, InventoryItem, Warehouse, Category
from apps.orders.models import PurchaseOrder
from .models import DashboardMetrics, SupplierPerformance, CategoryAnalytics, CostAnalysis
from .serializers import (
    DashboardMetricsSerializer, SupplierPerformanceSerializer,
    CategoryAnalyticsSerializer, CostAnalysisSerializer,
    ABCAnalysisSerializer, InventoryKPISerializer
)


class DashboardMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for DashboardMetrics model."""

    queryset = DashboardMetrics.objects.all()
    serializer_class = DashboardMetricsSerializer


class SupplierPerformanceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SupplierPerformance model."""

    queryset = SupplierPerformance.objects.select_related('supplier')
    serializer_class = SupplierPerformanceSerializer


class CategoryAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for CategoryAnalytics model."""

    queryset = CategoryAnalytics.objects.select_related('category')
    serializer_class = CategoryAnalyticsSerializer


class CostAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for CostAnalysis model."""

    queryset = CostAnalysis.objects.select_related('warehouse')
    serializer_class = CostAnalysisSerializer


class DashboardView(APIView):
    """Get current dashboard data."""

    def get(self, request):
        # Calculate real-time metrics
        inventory_items = InventoryItem.objects.select_related('product', 'warehouse')

        total_products = Product.objects.filter(is_active=True).count()
        total_warehouses = Warehouse.objects.filter(is_active=True).count()

        # Calculate inventory value
        total_value = sum(item.total_value for item in inventory_items)

        # Stock status counts
        out_of_stock = inventory_items.filter(quantity=0).count()
        low_stock = inventory_items.filter(
            quantity__gt=0,
            quantity__lte=F('product__reorder_point')
        ).count()

        # Pending orders
        pending_orders = PurchaseOrder.objects.filter(
            status__in=['pending', 'approved', 'ordered', 'shipped']
        ).count()

        # Calculate basic turnover (simplified)
        # In reality, this would use historical sales data
        turnover_rate = 8.4  # Placeholder

        # Stockout rate
        total_items = inventory_items.count() or 1
        stockout_rate = (out_of_stock / total_items) * 100

        return Response({
            'metrics': {
                'total_products': total_products,
                'total_warehouses': total_warehouses,
                'total_value': float(total_value),
                'turnover_rate': turnover_rate,
                'stockout_rate': round(stockout_rate, 2),
                'forecast_accuracy': 94.2,  # Would come from forecasting
                'pending_orders': pending_orders,
                'low_stock_items': low_stock,
                'out_of_stock_items': out_of_stock,
            },
            'generated_at': timezone.now().isoformat()
        })


class ABCAnalysisView(APIView):
    """Get ABC analysis of products."""

    def get(self, request):
        products = Product.objects.filter(is_active=True).annotate(
            total_stock=Sum('inventory_items__quantity'),
            total_value=Sum('inventory_items__quantity') * F('unit_cost')
        ).order_by('-total_value')

        total_products = products.count()
        if total_products == 0:
            return Response({'error': 'No products found'})

        total_value = products.aggregate(
            total=Sum(F('inventory_items__quantity') * F('unit_cost'))
        )['total'] or 0

        # Calculate thresholds (A = top 20%, B = next 30%, C = remaining 50%)
        a_count = int(total_products * 0.2) or 1
        b_count = int(total_products * 0.5) - a_count

        a_products = products[:a_count]
        b_products = products[a_count:a_count + b_count]
        c_products = products[a_count + b_count:]

        def calc_class_stats(prods, class_name):
            count = len(prods)
            value = sum(float(p.total_value or 0) for p in prods)
            return {
                'class_name': class_name,
                'product_count': count,
                'percentage': round((count / total_products) * 100, 1) if total_products else 0,
                'total_value': round(value, 2),
                'value_percentage': round((value / float(total_value)) * 100, 1) if total_value else 0
            }

        analysis = [
            calc_class_stats(a_products, 'A'),
            calc_class_stats(b_products, 'B'),
            calc_class_stats(c_products, 'C'),
        ]

        return Response({
            'analysis': analysis,
            'total_products': total_products,
            'total_value': float(total_value),
            'last_calculated': timezone.now().isoformat()
        })


class InventoryKPIView(APIView):
    """Get inventory KPIs."""

    def get(self, request):
        # Calculate KPIs
        inventory_items = InventoryItem.objects.select_related('product')
        total_items = inventory_items.count() or 1

        # Average inventory value
        avg_value = inventory_items.aggregate(
            avg=Avg(F('quantity') * F('product__unit_cost'))
        )['avg'] or 0

        # Total value
        total_value = sum(item.total_value for item in inventory_items)

        # Stockout rate
        out_of_stock = inventory_items.filter(quantity=0).count()
        stockout_rate = (out_of_stock / total_items) * 100

        # Fill rate (simplified - would need order data)
        fill_rate = 97.2

        # Order accuracy (simplified)
        order_accuracy = 99.1

        # Carrying cost (typically 20-30% of inventory value annually)
        carrying_cost = total_value * Decimal('0.25')

        # Inventory turnover (simplified)
        turnover = 8.4

        return Response({
            'inventory_turnover': turnover,
            'fill_rate': fill_rate,
            'stockout_rate': round(stockout_rate, 2),
            'average_inventory_value': float(avg_value),
            'total_inventory_value': float(total_value),
            'carrying_cost': float(carrying_cost),
            'order_accuracy': order_accuracy,
        })


class TrendAnalysisView(APIView):
    """Get trend data for charts."""

    def get(self, request):
        period = request.query_params.get('period', '30d')

        if period == '7d':
            days = 7
        elif period == '90d':
            days = 90
        elif period == '1y':
            days = 365
        else:
            days = 30

        # Get historical metrics
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        metrics = DashboardMetrics.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')

        # If no historical data, generate sample data
        if not metrics.exists():
            # Generate sample trend data
            data = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                data.append({
                    'date': date.isoformat(),
                    'inventory_value': 4000000 + (i * 5000),
                    'turnover_rate': 8.0 + (i * 0.01),
                    'stockout_rate': 3.0 - (i * 0.02),
                    'order_count': 10 + (i % 5),
                })
            return Response({'trends': data, 'period': period})

        return Response({
            'trends': DashboardMetricsSerializer(metrics, many=True).data,
            'period': period
        })


class SupplierScoreboardView(APIView):
    """Get supplier performance scoreboard."""

    def get(self, request):
        from apps.inventory.models import Supplier

        suppliers = Supplier.objects.filter(is_active=True)
        scoreboard = []

        for supplier in suppliers:
            # Get latest performance record
            perf = SupplierPerformance.objects.filter(
                supplier=supplier
            ).order_by('-period_end').first()

            if perf:
                scoreboard.append({
                    'supplier_id': supplier.id,
                    'supplier_name': supplier.name,
                    'on_time_rate': float(perf.on_time_rate),
                    'quality_rate': float(perf.quality_rate),
                    'average_lead_time': float(perf.average_lead_time),
                    'overall_score': float(perf.overall_score),
                    'total_orders': perf.total_orders,
                })
            else:
                # Use default values
                scoreboard.append({
                    'supplier_id': supplier.id,
                    'supplier_name': supplier.name,
                    'on_time_rate': float(supplier.reliability_score),
                    'quality_rate': 99.0,
                    'average_lead_time': float(supplier.lead_time_days),
                    'overall_score': float(supplier.reliability_score) * 0.95,
                    'total_orders': 0,
                })

        # Sort by overall score
        scoreboard.sort(key=lambda x: x['overall_score'], reverse=True)

        return Response({
            'scoreboard': scoreboard,
            'generated_at': timezone.now().isoformat()
        })
