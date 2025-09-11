
from celery import Celery

# Create a Celery instance
celery_app = Celery(
    "backendbot",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["src.backendbot.tasks"],
)

# Optional configuration
celery_app.conf.update(
    result_expires=3600,
)

if __name__ == "__main__":
    celery_app.start()
