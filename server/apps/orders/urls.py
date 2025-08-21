"""URL routes for orders app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PurchaseOrderViewSet, PurchaseOrderItemViewSet, OrderHistoryViewSet

router = DefaultRouter()
router.register('purchase-orders', PurchaseOrderViewSet)
router.register('items', PurchaseOrderItemViewSet)
router.register('history', OrderHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
