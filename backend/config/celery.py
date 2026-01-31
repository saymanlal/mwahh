import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'expire-chats': {
        'task': 'api.tasks.expire_chats',
        'schedule': crontab(minute='*/15'),
    },
    'send-payment-reminders': {
        'task': 'api.tasks.send_payment_reminders',
        'schedule': crontab(hour='9', minute='0'),
    },
    'cleanup-expired-otps': {
        'task': 'api.tasks.cleanup_expired_otps',
        'schedule': crontab(hour='*/6'),
    },
    'cleanup-unverified-users': {
        'task': 'api.tasks.cleanup_unverified_users',
        'schedule': crontab(hour='2', minute='0'),
    },
    'cleanup-expired-matches': {
        'task': 'api.tasks.cleanup_expired_matches',
        'schedule': crontab(hour='3', minute='0'),
    },
    'cleanup-deleted-chats': {
        'task': 'api.tasks.cleanup_deleted_chats',
        'schedule': crontab(day_of_week='0', hour='4', minute='0'),
    },
    'verify-subscriptions': {
        'task': 'api.tasks.verify_subscriptions',
        'schedule': crontab(minute='*/30'),
    },
    'cleanup-typing-indicators': {
        'task': 'api.tasks.cleanup_typing_indicators',
        'schedule': crontab(minute='*/5'),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
