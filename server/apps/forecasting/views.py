"""Views for forecasting app."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from datetime import datetime, timedelta

from apps.inventory.models import Product
from .models import DemandHistory, DemandForecast, ForecastAccuracy, SeasonalityPattern
from .serializers import (
    DemandHistorySerializer, DemandForecastSerializer,
    ForecastAccuracySerializer, SeasonalityPatternSerializer,
    ForecastRequestSerializer, ForecastResultSerializer,
    BulkForecastRequestSerializer
)
from .services import ForecastingService


class DemandHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for DemandHistory model."""

    queryset = DemandHistory.objects.select_related('product')
    serializer_class = DemandHistorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'is_promotion', 'is_holiday']

    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Bulk upload demand history data."""
        data = request.data.get('records', [])
        created_count = 0
        errors = []

        for record in data:
            serializer = DemandHistorySerializer(data=record)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                errors.append({'record': record, 'errors': serializer.errors})

        return Response({
            'created': created_count,
            'errors': errors
        })


class DemandForecastViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for DemandForecast model."""

    queryset = DemandForecast.objects.select_related('product')
    serializer_class = DemandForecastSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'model_type']


class ForecastAccuracyViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ForecastAccuracy model."""

    queryset = ForecastAccuracy.objects.select_related('product')
    serializer_class = ForecastAccuracySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'model_type']


class SeasonalityPatternViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SeasonalityPattern model."""

    queryset = SeasonalityPattern.objects.select_related('product')
    serializer_class = SeasonalityPatternSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'pattern_type']


class GenerateForecastView(APIView):
    """Generate demand forecast for a product."""

    def post(self, request):
        serializer = ForecastRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        product_id = data['product_id']

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Generate forecast using service
        service = ForecastingService()
        result = service.generate_forecast(
            product=product,
            horizon_weeks=data['horizon_weeks'],
            model_type=data['model_type'],
            confidence_level=float(data['confidence_level'])
        )

        return Response(result)


class BulkForecastView(APIView):
    """Generate forecasts for multiple products."""

    def post(self, request):
        serializer = BulkForecastRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        product_ids = data.get('product_ids', [])

        if product_ids:
            products = Product.objects.filter(id__in=product_ids, is_active=True)
        else:
            products = Product.objects.filter(is_active=True)

        service = ForecastingService()
        results = []

        for product in products:
            try:
                result = service.generate_forecast(
                    product=product,
                    horizon_weeks=data['horizon_weeks'],
                    model_type=data['model_type']
                )
                results.append(result)
            except Exception as e:
                results.append({
                    'product_id': product.id,
                    'product_sku': product.sku,
                    'error': str(e)
                })

        return Response({
            'total_products': len(products),
            'successful': len([r for r in results if 'error' not in r]),
            'results': results
        })


class ForecastSummaryView(APIView):
    """Get forecast summary and model performance."""

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get latest forecasts
        forecasts = DemandForecast.objects.filter(
            product=product,
            forecast_date__gte=datetime.now().date()
        ).order_by('forecast_date')[:12]

        # Get accuracy metrics
        accuracy = ForecastAccuracy.objects.filter(
            product=product
        ).order_by('-calculated_at').first()

        # Get seasonality
        seasonality = SeasonalityPattern.objects.filter(
            product=product,
            pattern_type='monthly'
        ).order_by('period_index')

        # Calculate summary stats
        if forecasts.exists():
            total_demand = sum(f.predicted_demand for f in forecasts)
            avg_demand = total_demand / len(forecasts)
            peak = max(forecasts, key=lambda f: f.predicted_demand)
        else:
            total_demand = 0
            avg_demand = 0
            peak = None

        return Response({
            'product': {
                'id': product.id,
                'sku': product.sku,
                'name': product.name,
            },
            'summary': {
                'total_forecasted_demand': float(total_demand),
                'average_weekly_demand': float(avg_demand),
                'peak_demand_date': peak.forecast_date if peak else None,
                'peak_demand_value': float(peak.predicted_demand) if peak else None,
            },
            'accuracy': ForecastAccuracySerializer(accuracy).data if accuracy else None,
            'forecasts': DemandForecastSerializer(forecasts, many=True).data,
            'seasonality': SeasonalityPatternSerializer(seasonality, many=True).data,
        })
