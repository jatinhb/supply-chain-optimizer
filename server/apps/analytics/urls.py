"""URL routes for analytics app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DashboardMetricsViewSet, SupplierPerformanceViewSet,
    CategoryAnalyticsViewSet, CostAnalysisViewSet,
    DashboardView, ABCAnalysisView, InventoryKPIView,
    TrendAnalysisView, SupplierScoreboardView
)

router = DefaultRouter()
router.register('metrics', DashboardMetricsViewSet)
router.register('supplier-performance', SupplierPerformanceViewSet)
router.register('category-analytics', CategoryAnalyticsViewSet)
router.register('costs', CostAnalysisViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('abc-analysis/', ABCAnalysisView.as_view(), name='abc_analysis'),
    path('kpis/', InventoryKPIView.as_view(), name='inventory_kpis'),
    path('trends/', TrendAnalysisView.as_view(), name='trends'),
    path('supplier-scoreboard/', SupplierScoreboardView.as_view(), name='supplier_scoreboard'),
]
