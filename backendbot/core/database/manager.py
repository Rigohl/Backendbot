"""
Database manager for BackendBot.
"""
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from .models import engine, SessionLocal

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DatabaseManager:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal

    def get_settings(self):
        with get_db() as db:
            # Implement logic to get settings
            pass

    def save_settings(self, settings):
        with get_db() as db:
            # Implement logic to save settings
            pass

    def log_metric(self, metric_data):
        with get_db() as db:
            db.add(metric_data)
            db.commit()

    def get_metrics(self, limit=100):
        with get_db() as db:
            # Implement logic to get metrics
            pass
