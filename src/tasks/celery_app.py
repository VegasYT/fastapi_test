# Запуск celery
# celery -A src.tasks.celery_app:celery_instance worker -l INFO --pool=solo

from celery import Celery

from src.config import settings

celery_instance = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    include=[
        "src.tasks.tasks",
    ],
)
