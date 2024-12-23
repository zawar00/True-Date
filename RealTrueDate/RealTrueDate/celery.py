from __future__ import absolute_import, unicode_literals
from celery import Celery
import os

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RealTrueDate.settings')

app = Celery('RealTrueDate')

# Configure Celery using Django settings, with a namespace prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Use the 'solo' pool to avoid issues with multiprocessing on Windows (for debugging only).
# For production, you should use a message broker and configure the proper pool (e.g., threads or prefork).
app.conf.update(
    worker_pool='solo',
)

# Automatically discover tasks from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
