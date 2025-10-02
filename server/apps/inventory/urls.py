"""URL routes for inventory app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SupplierViewSet, WarehouseViewSet, CategoryViewSet,
    ProductViewSet, InventoryItemViewSet, StockMovementViewSet
)

router = DefaultRouter()
router.register('suppliers', SupplierViewSet)
router.register('warehouses', WarehouseViewSet)
router.register('categories', CategoryViewSet)
router.register('products', ProductViewSet)
router.register('items', InventoryItemViewSet)
router.register('movements', StockMovementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
