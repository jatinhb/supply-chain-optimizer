"""Admin configuration for orders app."""
from django.contrib import admin
from .models import PurchaseOrder, PurchaseOrderItem, OrderHistory


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'warehouse', 'status', 'priority', 'total_amount', 'created_at']
    list_filter = ['status', 'priority', 'supplier', 'warehouse']
    search_fields = ['order_number', 'supplier__name']
    inlines = [PurchaseOrderItemInline]


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'from_status', 'to_status', 'changed_by', 'created_at']
    list_filter = ['to_status', 'created_at']
    search_fields = ['order__order_number']
