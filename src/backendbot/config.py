import os
from typing import Dict, List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


import secrets # Import secrets module for JWT_SECRET_KEY

class Settings(BaseSettings):
    # CPU/RAM thresholds with validation
    CPU_THRESHOLD: int = Field(default=80, ge=1, le=100, description="CPU usage threshold percentage")
    RAM_THRESHOLD: int = Field(default=4000, ge=100, description="RAM usage threshold in MB")

    # Timing
    CHECK_TIME: int = Field(default=60, ge=10, description="Check interval in seconds")
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    # Process lists
    HIBERNABLES: List[str] = Field(default_factory=lambda: ["Discord.exe", "Steam.exe"])
    PROCESOS_A_CERRAR: Dict[str, List[str]] = Field(default_factory=dict)
    PROCESOS_IMPORTANTES: List[str] = Field(default_factory=lambda: ["explorer.exe", "chrome.exe"])

    # Mode
    MODO: str = Field(default="diario", pattern="^(diario|videojuego|editor|streaming|multimedia)$")

    # API and security - MADE REQUIRED
    API_KEY: str = Field(default="backendbot_default_key_2024", description="API key for authentication")
    ADMIN_USERNAME: str = Field(default="admin", description="Admin username for dashboard access")
    ADMIN_PASSWORD: str = Field(default="admin123", description="Admin password for dashboard access")
    JWT_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), description="JWT secret key") # Generate if not provided
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

    # Optional dependencies flags (computed at runtime)
    GPU_AVAILABLE: bool = Field(default=False)
    WMI_AVAILABLE: bool = Field(default=False)

    # Railway/Deployment configuration
    PORT: Optional[int] = Field(default=8000, description="Puerto del servidor")
    HOST: str = Field(default="0.0.0.0", description="Host del servidor")
    RAILWAY_ENVIRONMENT: str = Field(default="development", description="Entorno de Railway")
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API Key")
    LOG_LEVEL: str = Field(default="INFO", description="Nivel de logging")

    # Activity monitoring configuration
    ACTIVITY_MONITORING_ENABLED: bool = Field(default=True, description="Habilitar monitoreo de actividad del usuario")
    INACTIVITY_WARNING_TIME: int = Field(default=300, ge=60, description="Tiempo de inactividad antes de mostrar advertencia (segundos)")
    INACTIVITY_SHUTDOWN_TIME: int = Field(default=480, ge=60, description="Tiempo total de inactividad antes de apagar backend (segundos)")
    ACTIVITY_CHECK_INTERVAL: int = Field(default=1, ge=1, description="Intervalo para verificar actividad (segundos)")
    BACKEND_AUTO_START: bool = Field(default=True, description="Iniciar backend automáticamente al detectar actividad")
    BACKEND_AUTO_STOP: bool = Field(default=True, description="Apagar backend automáticamente por inactividad")
    SUSPENSION_THRESHOLD: int = Field(default=3, ge=1, description="Umbral de suspensiones antes de tomar acción")
    REJECTION_THRESHOLD: int = Field(default=3, ge=1, description="Umbral de rechazos antes de tomar acción")

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

    # Rate limiting configuration
    RATE_LIMIT_WINDOW: int = Field(default=60, ge=1, description="Ventana de tiempo para rate limiting en segundos")
    RATE_LIMIT_REQUESTS: int = Field(default=100, ge=1, description="Número máximo de requests por ventana de tiempo")

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
        # Check optional dependencies before calling super().__init__
        gpu_available = False
        wmi_available = False
        
        try:
            import GPUtil
            gpu_available = True
        except ImportError:
            gpu_available = False

        try:
            import wmi
            wmi_available = True
        except ImportError:
            wmi_available = False
            
        # Add the computed values to kwargs
        kwargs['GPU_AVAILABLE'] = gpu_available
        kwargs['WMI_AVAILABLE'] = wmi_available
        
        super().__init__(**kwargs)


# Global settings instance
settings = Settings()
