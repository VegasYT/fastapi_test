# Запуск celery
# celery -A src.tasks.celery_app:celery_instance worker -l INFO --pool=solo
# Запуск celery beat
# celery -A src.tasks.celery_app:celery_instance beat -l INFO

from celery import Celery

from src.config import settings
# import src.tasks.tasks


celery_instance = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    include=[
        "src.tasks.tasks",
    ],
)

celery_instance.conf.beat_schedule = {
    "luboe-nazvanie": {
        "task": "booking_today_checkin",
        "schedule": 5,
    }
}