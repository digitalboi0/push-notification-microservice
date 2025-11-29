# Import the Celery app instance so it's available when 'push' is imported
from .celery import app as celery_app

__all__ = ('celery_app',)