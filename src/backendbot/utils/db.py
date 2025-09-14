from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.backendbot.config import settings

# Intentar importar psycopg2, pero no fallar si no está disponible
try:
    import psycopg2
    print("✅ psycopg2 importado correctamente")
except ImportError as e:
    print(f"⚠️  psycopg2 no disponible: {e}")
    print("Continuando sin psycopg2 explícito...")

# Crear engine con configuración optimizada para Railway
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_recycle=300,    # Reciclar conexiones cada 5 minutos
    echo=False           # Desactivar logs de SQL en producción
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()