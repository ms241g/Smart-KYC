from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "kyc",
    broker=settings.redis_broker_url,
    backend=settings.redis_backend_url,
)

celery_app.autodiscover_tasks(["app.workflows"])
