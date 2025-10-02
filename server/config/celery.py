"""
Celery configuration for SupplyChainIQ project.
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('supplychain')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Scheduled tasks
app.conf.beat_schedule = {
    'update-forecasts-daily': {
        'task': 'apps.forecasting.tasks.update_all_forecasts',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
    },
    'check-reorder-points': {
        'task': 'apps.inventory.tasks.check_reorder_points',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'calculate-abc-analysis': {
        'task': 'apps.analytics.tasks.calculate_abc_analysis',
        'schedule': crontab(hour=3, minute=0, day_of_week=1),  # Weekly on Monday
    },
}
