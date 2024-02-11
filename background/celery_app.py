from datetime import timedelta

from celery import Celery

# Инициализация Celery
celery_app = Celery(
    'worker',
    broker='amqp://guest:guest@localhost',  # URL для RabbitMQ
    # backend='rpc://',
    include=['background.tasks']  # Указываем, где искать задачи Celery
)

celery_app.conf.beat_schedule = {
    'update_menu_every_15_seconds': {
        'task': 'update_menu_from_sheet',
        'schedule': timedelta(seconds=15),  # Настройте для выполнения каждые 15 секунд
    },
}
