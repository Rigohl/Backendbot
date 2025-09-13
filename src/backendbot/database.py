from collections.abc import AsyncGenerator

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, ForeignKey
from sqlalchemy.types import JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

from .config import settings

# --- DB setup ---
# Adjust DATABASE_URL for aiosqlite if it's a sqlite path
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("sqlite:///"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

# Crear engine solo si hay una URL de base de datos válida
async_engine = None
AsyncSessionLocal = None

if DATABASE_URL and DATABASE_URL != "sqlite:///":
    try:
        # Set echo to False for production
        async_engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)
        AsyncSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
        )
    except Exception as e:
        print(f"Error configurando base de datos: {e}")
        async_engine = None

Base = declarative_base()


# Add a to_dict method to the Base class for easy serialization
def to_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}


Base.to_dict = to_dict


class ProcessHistory(Base):
    __tablename__ = "process_history"
    id = Column(Integer, primary_key=True)
    timestamp = Column(Float)
    pid = Column(Integer)
    name = Column(String)
    ram_mb = Column(Float)
    cpu_percent = Column(Float)


class OptimizationEvent(Base):
    __tablename__ = "optimization_events"
    id = Column(Integer, primary_key=True)
    timestamp = Column(Float)
    freed_ram_mb = Column(Float)


class WatchdogDecision(Base):
    __tablename__ = "watchdog_decisions"
    id = Column(Integer, primary_key=True)
    timestamp = Column(Float)
    program_name = Column(String)
    action = Column(String)
    cpu_usage = Column(Float, nullable=True)
    ram_usage = Column(Float, nullable=True)


class DecisionMemory(Base):
    __tablename__ = "decision_memory"
    program_name = Column(String, primary_key=True, index=True)
    suspensions = Column(Integer, default=0)
    rejections = Column(Integer, default=0)


class AIConversation(Base):
    __tablename__ = "ai_conversations"
    id = Column(String, primary_key=True, index=True)
    model = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    context = Column(JSON, nullable=True)
    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan")


class AIMessage(Base):
    __tablename__ = "ai_messages"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(String, ForeignKey("ai_conversations.id"))
    role = Column(String)
    content = Column(String)
    timestamp = Column(DateTime)
    metadata_ = Column(JSON, nullable=True) # Renamed to metadata_ to avoid conflict with Python keyword
    conversation = relationship("AIConversation", back_populates="messages")


class AIAgent(Base):
    __tablename__ = "ai_agents"
    name = Column(String, primary_key=True, index=True)
    description = Column(String)
    capabilities = Column(JSON) # Store as JSON array
    model = Column(String)
    created_at = Column(DateTime)
    system_prompt = Column(String)


async def init_db():
    if async_engine:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if AsyncSessionLocal:
        async with AsyncSessionLocal() as session:
            yield session