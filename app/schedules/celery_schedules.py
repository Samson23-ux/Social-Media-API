from celery.schedules import crontab

from app.schedules.celery_app import app


app.conf.beat_schedule = {
    'delete_users' : {
        'task': 'app.schedules.celery_task.delete_accounts',
        'schedule': crontab(hour=15, minute=0)
    }
}


app.conf.beat_schedule = {
    'delete_refresh_tokens' : {
        'task': 'app.schedules.celery_task.delete_refresh_tokens',
        'schedule': crontab(day_of_month=[15], hour=15, minute=0)
    }
}
