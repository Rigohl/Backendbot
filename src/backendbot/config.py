import os
from typing import Dict, List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CPU_THRESHOLD: int = 80
    RAM_THRESHOLD: int = 4000  # en MB
    RAM_WARNING_THRESHOLD_PERCENT: int = 70 # New: Warning threshold for RAM usage percentage
    RAM_CRITICAL_THRESHOLD_PERCENT: int = 90 # New: Critical threshold for RAM usage percentage
    CHECK_TIME: int = 60  # en segundos
    HIBERNABLES: List[str] = ["Discord.exe", "Steam.exe", "RiotClientServices.exe"]
    MODO: str = "diario"
    PROCESOS_A_CERRAR: Dict[str, List[str]] = {
        "videojuego": [
            "Discord.exe",
            "Steam.exe",
            "RiotClientServices.exe",
            "chrome.exe",
            "firefox.exe",
            "msedge.exe",
            "spotify.exe",
            "vlc.exe",
        ],
        "editor": [
            "chrome.exe",
            "firefox.exe",
            "msedge.exe",
            "discord.exe",
            "steam.exe",
        ],
        "diario": [
            "Code.exe",
            "Code - Insiders.exe",
            "electron.exe",
            "github.exe",
            "copilot.exe",
            "cmd.exe",
            "powershell.exe",
        ],
        "streaming": [
            "Code.exe",
            "Steam.exe",
            "Guild Wars 2.exe",
            "DaVinci Resolve.exe",
            "Visual Studio.exe",
            "CMake.exe",
            "Cheat Engine.exe",
        ],
        "multimedia": [
            "Guild Wars 2.exe",
            "Steam.exe",
            "Discord.exe",
            "chrome.exe",
            "firefox.exe",
            "msedge.exe",
            "OBS.exe",
            "Spotify.exe",
        ],
    }
    PROCESOS_IMPORTANTES: List[str] = [
        "explorer.exe",
        "obs.exe",
        "DaVinci Resolve.exe",
        "Fairlight.exe",
        "chrome.exe",
        "firefox.exe",
        "msedge.exe",
        "Discord.exe",
        "Spotify.exe",
    ]
    API_KEY: str = "your-super-secret-api-key"

    # Neon/SQLite DB config
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///"
        + os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "..",
            "data",
            "backend_data.db",
        ),
    )

    # File paths
    LOG_FILE: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs", "backend.log"
    )
    MEMORY_FILE: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "memory.json"
    )
    DB_FILE: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "data",
        "backend_data.db",
    )

    # Watchdog thresholds
    SUSPENSION_THRESHOLD: int = 3  # Número de suspensiones antes de ignorar
    REJECTION_THRESHOLD: int = 3  # Número de rechazos antes de ignorar

    model_config = SettingsConfigDict(env_file="config/.env", env_file_encoding="utf-8")


settings = Settings()
