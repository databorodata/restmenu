from datetime import timedelta

from celery import Celery

from app.config import RABBITMQ_HOST

# Инициализация Celery
celery_app = Celery(
    'worker',
    broker=f'amqp://guest:guest@{RABBITMQ_HOST}',
    include=['background.tasks']
)

celery_app.conf.beat_schedule = {
    'update_menu_every_15_seconds': {
        'task': 'update_menu_from_sheet',
        'schedule': timedelta(seconds=15),
    },
}
