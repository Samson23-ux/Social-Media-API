from celery.schedules import crontab

from app.schedules.celery_app import app



app.conf.beat_schedule = {
    'delete_tokens': {
        'task': 'app.schedules.celery_tasks.delete_refresh_tokens',
        'schedule': crontab(hour=15, minute=0)
    },

    'delete_users': {
        'task': 'app.schedules.celery_tasks.delete_users',
        'schedule': crontab(day_of_month=15, hour=18, minute=0)
    },
}
