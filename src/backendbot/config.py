import os
from typing import Dict, List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # CPU/RAM thresholds with validation
    CPU_THRESHOLD: int = Field(default=80, ge=1, le=100, description="CPU usage threshold percentage")
    RAM_THRESHOLD: int = Field(default=4000, ge=100, description="RAM usage threshold in MB")

    # Timing
    CHECK_TIME: int = Field(default=60, ge=10, description="Check interval in seconds")

    # Process lists
    HIBERNABLES: List[str] = Field(default_factory=lambda: ["Discord.exe", "Steam.exe"])
    PROCESOS_A_CERRAR: Dict[str, List[str]] = Field(default_factory=dict)
    PROCESOS_IMPORTANTES: List[str] = Field(default_factory=lambda: ["explorer.exe", "chrome.exe"])

    # Mode
    MODO: str = Field(default="diario", pattern="^(diario|videojuego|editor|streaming|multimedia)$")

    # API and security
    API_KEY: str = Field(default="default-api-key", description="API key for authentication")
    JWT_SECRET_KEY: str = Field(default="your-secret-key")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = Field(
        default_factory=lambda: f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'backend_data.db')}",
        env="DATABASE_URL"
    )

    # File paths
    LOG_FILE: str = Field(
        default_factory=lambda: os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs", "backend.log")
    )
    MEMORY_FILE: str = Field(
        default_factory=lambda: os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "memory.json")
    )

    # Optional dependencies flags
    GPU_AVAILABLE: bool = Field(default=False)
    WMI_AVAILABLE: bool = Field(default=False)

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, ge=1)
    RATE_LIMIT_WINDOW: int = Field(default=60, ge=1)  # seconds

    # Watchdog thresholds
    SUSPENSION_THRESHOLD: int = Field(default=3, ge=1, description="Número de suspensiones antes de ignorar")
    REJECTION_THRESHOLD: int = Field(default=3, ge=1, description="Número de rechazos antes de ignorar")

    # AI Configuration
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="URL base para Ollama API")
    DEFAULT_AI_MODEL: str = Field(default="llama2", description="Modelo de IA por defecto")
    AI_ENABLED: bool = Field(default=True, description="Habilitar funcionalidades de IA")
    AI_ANALYSIS_INTERVAL: int = Field(default=300, ge=60, description="Intervalo para análisis de IA (segundos)")
    AI_MAX_CONVERSATIONS: int = Field(default=100, description="Máximo número de conversaciones a mantener")
    AI_AUTO_ANALYZE: bool = Field(default=True, description="Análisis automático del sistema con IA")

    # Logging configuration
    LOGGING_CONFIG: dict = Field(default_factory=lambda: {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": "INFO",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                "filename": os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..",
                    "..",
                    "logs",
                    "backend.log",
                ),
                "maxBytes": 10485760,  # 10 MB
                "backupCount": 5,
                "level": "INFO",
            },
        },
        "loggers": {
            "backendbot": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
    })

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @field_validator("PROCESOS_A_CERRAR", mode="before")
    @classmethod
    def set_default_processos_a_cerrar(cls, v):
        if not v:
            return {
                "videojuego": ["Discord.exe", "Steam.exe", "chrome.exe"],
                "editor": ["chrome.exe", "discord.exe"],
                "diario": ["Code.exe", "powershell.exe"],
                "streaming": ["Code.exe", "Steam.exe"],
                "multimedia": ["chrome.exe", "vlc.exe"]
            }
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Check optional dependencies
        try:
            import GPUtil
            self.GPU_AVAILABLE = True
        except ImportError:
            self.GPU_AVAILABLE = False

        try:
            import wmi
            self.WMI_AVAILABLE = True
        except ImportError:
            self.WMI_AVAILABLE = False


# Global settings instance
settings = Settings()
