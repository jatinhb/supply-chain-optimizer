"""Views for orders app."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db import transaction

from .models import PurchaseOrder, PurchaseOrderItem, OrderHistory
from .serializers import (
    PurchaseOrderSerializer, PurchaseOrderDetailSerializer,
    PurchaseOrderCreateSerializer, PurchaseOrderItemSerializer,
    OrderHistorySerializer, ApproveOrderSerializer, ReceiveItemsSerializer
)
from apps.inventory.models import InventoryItem, StockMovement


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for PurchaseOrder model."""

    queryset = PurchaseOrder.objects.select_related('supplier', 'warehouse', 'created_by')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['supplier', 'warehouse', 'status', 'priority']
    search_fields = ['order_number', 'supplier__name']
    ordering_fields = ['created_at', 'expected_delivery', 'total_amount']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PurchaseOrderDetailSerializer
        if self.action == 'create':
            return PurchaseOrderCreateSerializer
        return PurchaseOrderSerializer

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit order for approval."""
        order = self.get_object()

        if order.status != 'draft':
            return Response(
                {'error': 'Only draft orders can be submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self._change_status(order, 'pending', request.user, 'Submitted for approval')
        return Response(PurchaseOrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a pending order."""
        order = self.get_object()
        serializer = ApproveOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if order.status != 'pending':
            return Response(
                {'error': 'Only pending orders can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.approved_by = request.user
        order.approved_at = timezone.now()
        order.save(update_fields=['approved_by', 'approved_at'])

        self._change_status(
            order, 'approved', request.user,
            serializer.validated_data.get('notes', 'Order approved')
        )
        return Response(PurchaseOrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a pending order."""
        order = self.get_object()
        serializer = ApproveOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if order.status != 'pending':
            return Response(
                {'error': 'Only pending orders can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self._change_status(
            order, 'cancelled', request.user,
            serializer.validated_data.get('notes', 'Order rejected')
        )
        return Response(PurchaseOrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def mark_ordered(self, request, pk=None):
        """Mark order as sent to supplier."""
        order = self.get_object()

        if order.status != 'approved':
            return Response(
                {'error': 'Only approved orders can be marked as ordered'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self._change_status(order, 'ordered', request.user, 'Order sent to supplier')
        return Response(PurchaseOrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def mark_shipped(self, request, pk=None):
        """Mark order as shipped by supplier."""
        order = self.get_object()

        if order.status != 'ordered':
            return Response(
                {'error': 'Only ordered items can be marked as shipped'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self._change_status(order, 'shipped', request.user, 'Shipment in transit')
        return Response(PurchaseOrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def receive(self, request, pk=None):
        """Receive items from order."""
        order = self.get_object()
        serializer = ReceiveItemsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if order.status not in ['ordered', 'shipped']:
            return Response(
                {'error': 'Can only receive items from ordered or shipped orders'},
                status=status.HTTP_400_BAD_REQUEST
            )

        items_data = serializer.validated_data['items']
        received_items = []

        for item_data in items_data:
            try:
                order_item = order.items.get(id=item_data['item_id'])
            except PurchaseOrderItem.DoesNotExist:
                continue

            receive_qty = min(
                item_data['quantity'],
                order_item.quantity - order_item.received_quantity
            )

            if receive_qty <= 0:
                continue

            # Update order item
            order_item.received_quantity += receive_qty
            order_item.save()

            # Update inventory
            inventory_item, _ = InventoryItem.objects.get_or_create(
                product=order_item.product,
                warehouse=order.warehouse,
                defaults={
                    'min_quantity': order_item.product.reorder_point,
                    'max_quantity': order_item.product.reorder_point * 3,
                }
            )
            inventory_item.quantity += receive_qty
            inventory_item.last_restocked = timezone.now()
            inventory_item.save()

            # Create stock movement
            StockMovement.objects.create(
                inventory_item=inventory_item,
                movement_type='in',
                quantity=receive_qty,
                reference=order.order_number,
                notes=f'Received from PO {order.order_number}',
                created_by=request.user
            )

            received_items.append({
                'product_sku': order_item.product.sku,
                'received': receive_qty,
                'total_received': order_item.received_quantity,
                'ordered': order_item.quantity
            })

        # Check if order is fully received
        all_received = all(item.is_fully_received for item in order.items.all())
        if all_received:
            order.actual_delivery = timezone.now().date()
            order.save(update_fields=['actual_delivery'])
            self._change_status(order, 'delivered', request.user, 'All items received')

        return Response({
            'order': PurchaseOrderSerializer(order).data,
            'received_items': received_items,
            'fully_received': all_received
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order."""
        order = self.get_object()

        if order.status in ['delivered', 'cancelled']:
            return Response(
                {'error': 'Cannot cancel a delivered or already cancelled order'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self._change_status(order, 'cancelled', request.user, 'Order cancelled')
        return Response(PurchaseOrderSerializer(order).data)

    def _change_status(self, order, new_status, user, notes=''):
        """Helper to change order status and log history."""
        old_status = order.status
        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])

        OrderHistory.objects.create(
            order=order,
            from_status=old_status,
            to_status=new_status,
            changed_by=user,
            notes=notes
        )


class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    """ViewSet for PurchaseOrderItem model."""

    queryset = PurchaseOrderItem.objects.select_related('order', 'product')
    serializer_class = PurchaseOrderItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['order', 'product']


class OrderHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for OrderHistory model (read-only)."""

    queryset = OrderHistory.objects.select_related('order', 'changed_by')
    serializer_class = OrderHistorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['order', 'to_status']
