import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_tracker.settings')

app = Celery('smart_tracker')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()



app.conf.beat_schedule = {
    "check-prices-every-minute": {
        "task": "tracker.tasks.check_all_products",
        "schedule": 60.0,  
    },
    "cleanup-old-price-history-daily": {
        "task": "tracker.tasks.cleanup_old_price_history",
        "schedule": 86400.0, 
    },
}