"""Views for inventory app."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import Supplier, Warehouse, Category, Product, InventoryItem, StockMovement
from .serializers import (
    SupplierSerializer, WarehouseSerializer, CategorySerializer,
    ProductSerializer, ProductListSerializer,
    InventoryItemSerializer, InventoryItemDetailSerializer,
    StockMovementSerializer, StockAdjustmentSerializer, ReorderAlertSerializer
)


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet for Supplier model."""

    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'country']
    search_fields = ['name', 'code', 'contact_name']
    ordering_fields = ['name', 'reliability_score', 'lead_time_days']


class WarehouseViewSet(viewsets.ModelViewSet):
    """ViewSet for Warehouse model."""

    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['is_active', 'country', 'city']
    search_fields = ['name', 'code', 'city']

    @action(detail=True, methods=['get'])
    def utilization(self, request, pk=None):
        """Get warehouse utilization details."""
        warehouse = self.get_object()
        items = warehouse.inventory_items.select_related('product')

        total_stock = items.aggregate(total=Sum('quantity'))['total'] or 0
        total_value = sum(item.total_value for item in items)

        return Response({
            'warehouse': WarehouseSerializer(warehouse).data,
            'total_stock': total_stock,
            'total_value': total_value,
            'utilization_percentage': warehouse.current_utilization,
            'items_count': items.count(),
        })


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category model."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'code']


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product model."""

    queryset = Product.objects.select_related('category', 'supplier')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'supplier', 'abc_class', 'is_active']
    search_fields = ['sku', 'name', 'description']
    ordering_fields = ['sku', 'name', 'unit_cost', 'unit_price', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    @action(detail=True, methods=['get'])
    def stock_levels(self, request, pk=None):
        """Get stock levels across all warehouses."""
        product = self.get_object()
        items = product.inventory_items.select_related('warehouse')

        data = [{
            'warehouse': item.warehouse.name,
            'warehouse_code': item.warehouse.code,
            'quantity': item.quantity,
            'available': item.available_quantity,
            'status': item.status,
            'location': item.location,
        } for item in items]

        total = items.aggregate(
            total_stock=Sum('quantity'),
            total_reserved=Sum('reserved_quantity')
        )

        return Response({
            'product': ProductListSerializer(product).data,
            'warehouses': data,
            'total_stock': total['total_stock'] or 0,
            'total_reserved': total['total_reserved'] or 0,
        })


class InventoryItemViewSet(viewsets.ModelViewSet):
    """ViewSet for InventoryItem model."""

    queryset = InventoryItem.objects.select_related('product', 'warehouse')
    serializer_class = InventoryItemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['warehouse', 'product__category', 'product__abc_class']
    search_fields = ['product__sku', 'product__name', 'location']
    ordering_fields = ['quantity', 'product__sku', 'last_restocked']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InventoryItemDetailSerializer
        return InventoryItemSerializer

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Adjust stock quantity."""
        item = self.get_object()
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        movement_type = data['movement_type']
        quantity = data['quantity']

        # Update stock
        if movement_type in ['out']:
            if item.quantity < quantity:
                return Response(
                    {'error': 'Insufficient stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            item.quantity -= quantity
            movement_qty = -quantity
        else:
            item.quantity += quantity
            movement_qty = quantity

        item.save()

        # Record movement
        movement = StockMovement.objects.create(
            inventory_item=item,
            movement_type=movement_type,
            quantity=movement_qty,
            reference=data.get('reference', ''),
            notes=data.get('notes', ''),
            created_by=request.user
        )

        return Response({
            'message': 'Stock adjusted successfully',
            'new_quantity': item.quantity,
            'movement': StockMovementSerializer(movement).data
        })

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get items below reorder point."""
        items = self.get_queryset().filter(
            quantity__lte=F('product__reorder_point')
        ).select_related('product', 'warehouse')

        serializer = InventoryItemSerializer(items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def reorder_alerts(self, request):
        """Get reorder alerts with suggestions."""
        items = self.get_queryset().filter(
            quantity__lte=F('product__reorder_point')
        ).select_related('product', 'warehouse')

        alerts = []
        for item in items:
            # Calculate priority
            if item.quantity == 0:
                priority = 'critical'
            elif item.quantity <= item.product.safety_stock:
                priority = 'high'
            else:
                priority = 'medium'

            # Suggested order quantity (EOQ or default)
            suggested_qty = item.product.economic_order_quantity or (
                item.product.reorder_point * 2
            )

            alerts.append({
                'product_id': item.product.id,
                'sku': item.product.sku,
                'product_name': item.product.name,
                'current_stock': item.quantity,
                'reorder_point': item.product.reorder_point,
                'suggested_quantity': suggested_qty,
                'estimated_cost': suggested_qty * item.product.unit_cost,
                'priority': priority,
                'warehouse': item.warehouse.name,
            })

        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2}
        alerts.sort(key=lambda x: priority_order.get(x['priority'], 3))

        return Response(alerts)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for StockMovement model (read-only)."""

    queryset = StockMovement.objects.select_related(
        'inventory_item__product', 'inventory_item__warehouse', 'created_by'
    )
    serializer_class = StockMovementSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['movement_type', 'inventory_item__product', 'inventory_item__warehouse']
    ordering_fields = ['created_at', 'quantity']
