from collections.abc import AsyncGenerator

from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

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
        AsyncSessionLocal = async_sessionmaker(
            autocommit=False, autoflush=False, bind=async_engine
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
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[float]
    pid: Mapped[int]
    name: Mapped[str]
    ram_mb: Mapped[float]
    cpu_percent: Mapped[float]


class OptimizationEvent(Base):
    __tablename__ = "optimization_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[float]
    freed_ram_mb: Mapped[float]


class WatchdogDecision(Base):
    __tablename__ = "watchdog_decisions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[float]
    program_name: Mapped[str]
    action: Mapped[str]
    cpu_usage: Mapped[float] = mapped_column(nullable=True)
    ram_usage: Mapped[float] = mapped_column(nullable=True)


async def init_db():
    if async_engine:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if AsyncSessionLocal:
        async with AsyncSessionLocal() as session:
            yield session