"""URL routes for forecasting app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DemandHistoryViewSet, DemandForecastViewSet,
    ForecastAccuracyViewSet, SeasonalityPatternViewSet,
    GenerateForecastView, BulkForecastView, ForecastSummaryView
)

router = DefaultRouter()
router.register('history', DemandHistoryViewSet)
router.register('forecasts', DemandForecastViewSet)
router.register('accuracy', ForecastAccuracyViewSet)
router.register('seasonality', SeasonalityPatternViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate/', GenerateForecastView.as_view(), name='generate_forecast'),
    path('generate/bulk/', BulkForecastView.as_view(), name='bulk_forecast'),
    path('summary/<int:product_id>/', ForecastSummaryView.as_view(), name='forecast_summary'),
]
