import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

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
        async_engine = create_async_engine(DATABASE_URL, echo=True)
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


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
