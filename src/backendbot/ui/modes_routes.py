"""
Router para gestión de modos de operación
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from src.backendbot.config import OperationMode
from src.backendbot.modes import mode_manager

router = APIRouter()

@router.get("/modes", tags=["Modes"])
def get_available_modes():
    """Obtener lista de modos disponibles"""
    modes = {
        "editor": {
            "name": "Editor",
            "description": "Optimizado para edición de código y desarrollo",
            "focus_processes": ["code.exe", "pycharm.exe", "vscode.exe"]
        },
        "streaming": {
            "name": "Streaming",
            "description": "Para streaming y grabación",
            "focus_processes": ["obs.exe", "streamlabs.exe", "discord.exe"]
        },
        "relax": {
            "name": "Relax",
            "description": "Para uso casual y navegación",
            "focus_processes": ["chrome.exe", "firefox.exe", "spotify.exe"]
        },
        "desarrollo": {
            "name": "Desarrollo",
            "description": "Para desarrollo intensivo y compilación",
            "focus_processes": ["code.exe", "pycharm.exe", "docker.exe", "git.exe"]
        },
        "gaming": {
            "name": "Gaming",
            "description": "Para gaming y aplicaciones de alto rendimiento",
            "focus_processes": ["steam.exe", "epicgameslauncher.exe", "battle.net.exe"]
        }
    }
    return {"modes": modes}

@router.get("/modes/current", tags=["Modes"])
def get_current_mode():
    """Obtener el modo actual"""
    return mode_manager.get_mode_info()

@router.post("/modes/{mode_name}", tags=["Modes"])
def set_operation_mode(mode_name: str):
    """Cambiar el modo de operación"""
    try:
        mode_map = {
            "editor": OperationMode.EDITOR,
            "streaming": OperationMode.STREAMING,
            "relax": OperationMode.RELAX,
            "desarrollo": OperationMode.DESARROLLO,
            "gaming": OperationMode.GAMING
        }

        if mode_name not in mode_map:
            raise HTTPException(status_code=400, detail=f"Modo no válido: {mode_name}")

        mode_manager.set_mode(mode_map[mode_name])

        return {
            "message": f"Modo cambiado a {mode_name}",
            "mode_info": mode_manager.get_mode_info()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cambiando modo: {str(e)}")

@router.get("/modes/status", tags=["Modes"])
def get_mode_status():
    """Obtener estado detallado del modo actual"""
    try:
        mode_info = mode_manager.get_mode_info()
        thresholds = mode_manager._configure_monitoring_thresholds()

        return {
            "current_mode": mode_info,
            "thresholds": thresholds,
            "monitoring_interval": mode_manager.get_monitoring_interval(),
            "should_cleanup": mode_manager.should_cleanup(),
            "should_optimize": mode_manager.should_optimize()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")