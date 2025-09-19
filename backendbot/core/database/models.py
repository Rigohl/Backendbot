"""
Database models for BackendBot.
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

Base = declarative_base()

class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(JSON, nullable=False)

class Metric(Base):
    __tablename__ = 'metrics'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    cpu_usage = Column(Float)
    ram_usage = Column(Float)
    disk_usage = Column(Float)
    network_usage = Column(Float)

class BotRun(Base):
    __tablename__ = 'bot_runs'
    id = Column(Integer, primary_key=True)
    bot_name = Column(String, nullable=False)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String)
    result = Column(JSON)

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    channel = Column(String)
    message = Column(String)
    priority = Column(String)
    is_read = Column(Integer, default=0)

class Backup(Base):
    __tablename__ = 'backups'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    backup_name = Column(String)
    strategy = Column(String)
    path = Column(String)
    size = Column(Float)
    integrity_hash = Column(String)

# Database setup
DATABASE_URL = "sqlite:///./backendbot.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)


def create_tables(bind_engine=None):
    """Compatibility wrapper to create all tables."""
    engine_to_use = bind_engine or engine
    Base.metadata.create_all(bind=engine_to_use)


def drop_tables(bind_engine=None):
    """Compatibility wrapper to drop all tables (use with care)."""
    engine_to_use = bind_engine or engine
    Base.metadata.drop_all(bind=engine_to_use)


def create_indexes(bind_engine=None):
    """Placeholder for index creation if needed. Currently no-op."""
    # SQLAlchemy typically creates indexes via metadata; implement if needed.
    return None

