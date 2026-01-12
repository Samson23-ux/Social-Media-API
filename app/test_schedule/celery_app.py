from celery import Celery

from app.core.config import settings

app = Celery('celery_app', broker=settings.BROKER_URL, include=['app.test_schedule.celery_tasks'])

app.config_from_object('app.test_schedule.celeryconfig')

from app.test_schedule import celery_schedule
