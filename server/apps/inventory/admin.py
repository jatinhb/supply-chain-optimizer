"""Admin configuration for inventory app."""
from django.contrib import admin
from .models import Supplier, Warehouse, Category, Product, InventoryItem, StockMovement


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'contact_name', 'lead_time_days', 'reliability_score', 'is_active']
    list_filter = ['is_active', 'country']
    search_fields = ['name', 'code', 'contact_name']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'city', 'country', 'capacity', 'is_active']
    list_filter = ['is_active', 'country']
    search_fields = ['name', 'code', 'city']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent']
    search_fields = ['name', 'code']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'category', 'supplier', 'unit_cost', 'unit_price', 'abc_class', 'is_active']
    list_filter = ['category', 'supplier', 'abc_class', 'is_active']
    search_fields = ['sku', 'name']


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'reserved_quantity', 'status', 'location']
    list_filter = ['warehouse', 'product__category']
    search_fields = ['product__sku', 'product__name', 'location']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['inventory_item', 'movement_type', 'quantity', 'reference', 'created_by', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['inventory_item__product__sku', 'reference']
