import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'koz_flow.settings')
app = Celery('koz_flow')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
import koz_flow.tasks