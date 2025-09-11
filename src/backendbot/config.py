from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Dict
import os

class Settings(BaseSettings):
    CPU_THRESHOLD: int = 80
    RAM_THRESHOLD: int = 4000 # en MB
    CHECK_TIME: int = 60 # en segundos
    HIBERNABLES: List[str] = ["Discord.exe", "Steam.exe", "RiotClientServices.exe"]
    MODO: str = "diario"
    PROCESOS_A_CERRAR: Dict[str, List[str]] = {
        "videojuego": ["Discord.exe", "Steam.exe", "RiotClientServices.exe", "chrome.exe", "firefox.exe", "msedge.exe", "spotify.exe", "vlc.exe"],
        "editor": ["chrome.exe", "firefox.exe", "msedge.exe", "discord.exe", "steam.exe"],
        "diario": ["Code.exe", "Code - Insiders.exe", "electron.exe", "github.exe", "copilot.exe", "cmd.exe", "powershell.exe"],
        "streaming": ["Code.exe", "Steam.exe", "Guild Wars 2.exe", "DaVinci Resolve.exe", "Visual Studio.exe", "CMake.exe", "Cheat Engine.exe"],
        "multimedia": ["Guild Wars 2.exe", "Steam.exe", "Discord.exe", "chrome.exe", "firefox.exe", "msedge.exe", "OBS.exe", "Spotify.exe"]
    }
    PROCESOS_IMPORTANTES: List[str] = ["explorer.exe", "obs.exe", "DaVinci Resolve.exe", "Fairlight.exe", "chrome.exe", "firefox.exe", "msedge.exe", "Discord.exe", "Spotify.exe"]
    API_KEY: str = "your-super-secret-api-key"

    DATABASE_URL: str = "sqlite:///./data/backend_data.db" # Default to SQLite, but can be overridden for PostgreSQL (e.g., postgresql://user:password@host:port/dbname)

    # File paths
    LOG_FILE: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs", "backend.log")
    MEMORY_FILE: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "memory.json")
    DB_FILE: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "backend_data.db")

    model_config = SettingsConfigDict(env_file='config/.env', env_file_encoding='utf-8')