"""
BackendBot - Configuración Centralizada
Configuración unificada para toda la aplicación escalable
"""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
import io
from pathlib import Path as _Path


class DatabaseSettings(BaseSettings):
    """Configuración de base de datos"""

    url: str = Field(
        default="postgresql://backendbot:password@localhost:5432/backendbot",
        env="DATABASE_URL",
    )
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")

    model_config = ConfigDict(extra="ignore")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")


class RedisSettings(BaseSettings):
    """Configuración de Redis"""

    url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    db: int = Field(default=0, env="REDIS_DB")


class APISettings(BaseSettings):
    """Configuración de la API"""

    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    workers: int = Field(default=4, env="API_WORKERS")
    reload: bool = Field(default=True, env="API_RELOAD")

    model_config = ConfigDict(extra="ignore")


class SecuritySettings(BaseSettings):
    """Configuración de seguridad"""

    secret_key: str = Field(
        default="your-secret-key-change-in-production", env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )


class MonitoringSettings(BaseSettings):
    """Configuración de monitoreo"""

    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")


class BotSettings(BaseSettings):
    """Configuración de bots"""

    enabled_bots: List[str] = Field(
        default=[
            "monitor",
            "organizer",
            "indexer",
            "guardian",
            "auditor_files",
            "auditor_programs",
        ],
        env="ENABLED_BOTS",
    )
    max_concurrent_bots: int = Field(default=3, env="MAX_CONCURRENT_BOTS")
    bot_timeout_seconds: int = Field(default=300, env="BOT_TIMEOUT_SECONDS")

    model_config = ConfigDict(extra="ignore")


class Settings(BaseSettings):
    """Configuración principal de BackendBot"""

    # Entorno
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")

    # Rutas
    base_dir: Path = Path(__file__).parent.parent.parent
    logs_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "logs"
    )
    data_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "data"
    )

    # Sub-configuraciones
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    api: APISettings = APISettings()
    security: SecuritySettings = SecuritySettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    bots: BotSettings = BotSettings()

    # Use Pydantic v2 style ConfigDict. We set an env prefix so
    # environment variables like `backendbot_database_url` map to
    # nested fields (`database.url`). We use `_` as the nested
    # delimiter because existing environment variables in dev
    # environments are flat with underscores.
    model_config = ConfigDict(
        env_prefix="BACKENDBOT_",
        env_nested_delimiter="_",
        env_file=".env",
        # Keep default encoding but implement a tolerant loader below
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Allow extra fields from .env to avoid validation errors
    )


_cached_settings: Settings | None = None


def get_settings() -> Settings:
    """Return a cached Settings instance. Create and validate on first call.

    This avoids instantiating Settings at import time which would raise
    validation errors during test collection if the environment is not
    prepared. Tests and application code should call `get_settings()`.
    """
    global _cached_settings
    if _cached_settings is None:
        # Ensure env file can be read even on systems with legacy encodings
        env_path = _Path(Settings.model_config.get("env_file", ".env"))
        if env_path.exists():
            try:
                # Try to read with UTF-8 first
                with io.open(env_path, "r", encoding="utf-8"):
                    pass
            except Exception:
                # Fallback: rewrite a temporary UTF-8 copy using latin-1 to preserve bytes
                try:
                    raw = env_path.read_bytes()
                    text = raw.decode("latin-1")
                    tmp_path = env_path.with_suffix(env_path.suffix + ".utf8.tmp")
                    tmp_path.write_text(text, encoding="utf-8")
                    # Point Pydantic to the temporary file by overriding model_config at runtime
                    Settings.model_config = Settings.model_config.copy()
                    Settings.model_config["env_file"] = str(tmp_path)
                except Exception:
                    # Last resort: ignore env file by pointing to a non-existent file
                    Settings.model_config = Settings.model_config.copy()
                    Settings.model_config["env_file"] = ".env.missing"

        _cached_settings = Settings()
        validate_configuration(_cached_settings)
    return _cached_settings


# Validar configuración al importar
def validate_configuration(s: Settings) -> bool:
    """Validate the provided Settings instance."""
    errors: list[str] = []

    # Validate directories
    if not s.logs_dir.exists():
        s.logs_dir.mkdir(parents=True, exist_ok=True)

    if not s.data_dir.exists():
        s.data_dir.mkdir(parents=True, exist_ok=True)

    # Critical config validation
    if s.environment not in ["development", "staging", "production"]:
        errors.append(f"Invalid environment: {s.environment}")

    if s.api.port < 1 or s.api.port > 65535:
        errors.append(f"Invalid API port: {s.api.port}")

    if s.security.secret_key == "your-secret-key-change-in-production":
        if s.environment == "production":
            errors.append("Secret key must be changed in production")

    if errors:
        raise ValueError(f"Configuration validation failed: {', '.join(errors)}")

    return True
