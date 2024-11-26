# RealTrueDate/celery.py
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RealTrueDate.settings')

app = Celery('RealTrueDate')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Use the 'solo' pool to avoid issues with multiprocessing on Windows
app.conf.update(
    task_pool='solo',
)

app.autodiscover_tasks()
