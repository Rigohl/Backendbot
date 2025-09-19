"""
BackendBot API - Configuration Router
Gestión de configuración del sistema
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backendbot.core.di.container import container

router = APIRouter(prefix="/api/v1/config", tags=["configuration"])

# Modelos de respuesta
class ConfigResponse(BaseModel):
    success: bool
    message: str
    config: Dict[str, Any]
    timestamp: datetime

class ConfigUpdateResponse(BaseModel):
    success: bool
    message: str
    updated_keys: list
    timestamp: datetime

@router.get("/", response_model=ConfigResponse)
async def get_full_config():
    """
    Obtener configuración completa del sistema.
    """
    try:
        config_manager = container.get_config_manager()
        config = config_manager.get_all_config()

        return ConfigResponse(
            success=True,
            message="Configuration retrieved successfully",
            config=config,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving configuration: {str(e)}")

@router.get("/{section}", response_model=ConfigResponse)
async def get_config_section(section: str):
    """
    Obtener sección específica de la configuración.
    """
    try:
        config_manager = container.get_config_manager()

        # Mapear nombres de sección a métodos del config manager
        section_mapping = {
            "database": "get_database_config",
            "api": "get_api_config",
            "logging": "get_logging_config",
            "security": "get_security_config",
            "bots": "get_bots_config",
            "ui": "get_ui_config"
        }

        if section not in section_mapping:
            raise HTTPException(status_code=404, detail=f"Configuration section '{section}' not found")

        method_name = section_mapping[section]
        if hasattr(config_manager, method_name):
            config = getattr(config_manager, method_name)()
        else:
            config = {}

        return ConfigResponse(
            success=True,
            message=f"Configuration section '{section}' retrieved successfully",
            config={section: config},
            timestamp=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving configuration section: {str(e)}")

@router.put("/", response_model=ConfigUpdateResponse)
async def update_config(config_updates: Dict[str, Any]):
    """
    Actualizar configuración del sistema.
    """
    try:
        config_manager = container.get_config_manager()
        updated_keys = []

        # Actualizar cada clave en la configuración
        for key, value in config_updates.items():
            try:
                config_manager.set_config_value(key, value)
                updated_keys.append(key)
            except Exception as e:
                # Log error but continue with other updates
                print(f"Error updating config key '{key}': {str(e)}")

        return ConfigUpdateResponse(
            success=True,
            message="Configuration updated successfully",
            updated_keys=updated_keys,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating configuration: {str(e)}")

@router.post("/reload")
async def reload_config():
    """
    Recargar configuración desde archivos.
    """
    try:
        config_manager = container.get_config_manager()
        config_manager.reload_config()

        return {
            "success": True,
            "message": "Configuration reloaded successfully",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading configuration: {str(e)}")

@router.get("/export")
async def export_config():
    """
    Exportar configuración actual a JSON.
    """
    try:
        config_manager = container.get_config_manager()
        config = config_manager.get_all_config()

        return {
            "success": True,
            "message": "Configuration exported successfully",
            "config": config,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting configuration: {str(e)}")

@router.post("/import")
async def import_config(config_data: Dict[str, Any]):
    """
    Importar configuración desde JSON.
    """
    try:
        config_manager = container.get_config_manager()
        updated_keys = []

        # Importar configuración
        for section, values in config_data.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    try:
                        config_manager.set_config_value(f"{section}.{key}", value)
                        updated_keys.append(f"{section}.{key}")
                    except Exception as e:
                        print(f"Error importing config key '{section}.{key}': {str(e)}")
            else:
                try:
                    config_manager.set_config_value(section, values)
                    updated_keys.append(section)
                except Exception as e:
                    print(f"Error importing config key '{section}': {str(e)}")

        return {
            "success": True,
            "message": "Configuration imported successfully",
            "updated_keys": updated_keys,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing configuration: {str(e)}")

@router.get("/validate")
async def validate_config():
    """
    Validar configuración actual.
    """
    try:
        config_manager = container.get_config_manager()
        is_valid, errors = config_manager.validate_config()

        return {
            "success": is_valid,
            "message": "Configuration validation completed",
            "valid": is_valid,
            "errors": errors,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating configuration: {str(e)}")