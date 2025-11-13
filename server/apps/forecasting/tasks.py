"""Celery tasks for forecasting app."""
from celery import shared_task
from datetime import datetime


@shared_task
def update_all_forecasts():
    """Update forecasts for all active products."""
    from apps.inventory.models import Product
    from .services import ForecastingService

    service = ForecastingService()
    products = Product.objects.filter(is_active=True)

    results = {
        'total': products.count(),
        'success': 0,
        'failed': 0,
        'errors': []
    }

    for product in products:
        try:
            service.generate_forecast(
                product=product,
                horizon_weeks=12,
                model_type='prophet'
            )
            results['success'] += 1
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'product_id': product.id,
                'sku': product.sku,
                'error': str(e)
            })

    return results


@shared_task
def update_product_forecast(product_id: int, model_type: str = 'prophet'):
    """Update forecast for a single product."""
    from apps.inventory.models import Product
    from .services import ForecastingService

    try:
        product = Product.objects.get(id=product_id)
        service = ForecastingService()
        result = service.generate_forecast(
            product=product,
            horizon_weeks=12,
            model_type=model_type
        )
        return {
            'success': True,
            'product_id': product_id,
            'result': result
        }
    except Product.DoesNotExist:
        return {
            'success': False,
            'error': f'Product {product_id} not found'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def cleanup_old_forecasts(days: int = 90):
    """Remove forecasts older than specified days."""
    from datetime import timedelta
    from .models import DemandForecast

    cutoff_date = datetime.now().date() - timedelta(days=days)
    deleted, _ = DemandForecast.objects.filter(
        forecast_date__lt=cutoff_date
    ).delete()

    return f"Deleted {deleted} old forecast records"
