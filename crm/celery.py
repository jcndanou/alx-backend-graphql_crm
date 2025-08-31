# crm/celery.py
import os
from celery import Celery

# Configure le module de settings de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

# Initialise l'application Celery
app = Celery('crm')

# Charge la configuration de Django, y compris CELERY_BEAT_SCHEDULE
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvre et charge les tâches depuis les applications Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')