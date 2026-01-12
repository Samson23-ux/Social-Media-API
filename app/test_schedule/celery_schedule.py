from celery.schedules import crontab

from app.test_schedule.celery_app import app

app.conf.beat_schedule = {
    'delete_acc': {
        'task': 'app.test_schedule.celery_tasks.delete_accounts',
        'schedule': crontab(hour=15, minute=0)
    }
}

app.conf.beat_schedule = {
    'delete_token': {
        'task': 'app.test_schedule.celery_tasks.delete_refresh_tokens',
        'schedule': crontab(hour=12, minute=45)
    }
}
