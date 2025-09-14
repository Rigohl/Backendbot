from sqlalchemy.orm import Session
from src.backendbot.utils.db import SessionLocal, engine
from src.backendbot.models import Base, SystemEvent, BotAction

def create_db_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def log_system_event(level: str, source: str, message: str, details: str = None):
    db = next(get_db())
    try:
        event = SystemEvent(level=level, source=source, message=message, details=details)
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    finally:
        db.close()

def log_bot_action(bot_name: str, action_type: str, status: str, target: str = None, result: str = None):
    db = next(get_db())
    try:
        action = BotAction(bot_name=bot_name, action_type=action_type, status=status, target=target, result=result)
        db.add(action)
        db.commit()
        db.refresh(action)
        return action
    finally:
        db.close()

# Asegurarse de que las tablas se creen al importar este módulo
try:
    create_db_tables()
except Exception as e:
    print(f"Warning: Could not create DB tables on import: {e}. DB might not be available.")
