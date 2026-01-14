from celery import Celery

from app.core.config import settings

app = Celery(
    'celery_app', broker=settings.BROKER_URL, include=['app.schedules.celery_tasks']
)

app.config_from_object('app.schedules.celeryconfig')


from app.schedules import celery_schedules
