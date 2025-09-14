from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
import json

from src.backendbot.utils.logging_config import logger
from src.backendbot.utils.db_messaging import send_command, get_bot_state

router = APIRouter(
    prefix="/api/v1/organizer",
    tags=["Organizer"],
)

class ScanCommand(BaseModel):
    path: str

class DeleteDuplicatesCommand(BaseModel):
    files: list[str]

@router.post("/scan")
async def start_scan_duplicates(command: ScanCommand):
    """Inicia un escaneo de duplicados en la ruta especificada."""
    logger.info(f"Comando recibido: Iniciar escaneo de duplicados en {command.path}")
    send_command(bot_name="Bot Organizer", command_type="scan_duplicates", payload={"path": command.path})
    return {"message": f"Escaneo de duplicados iniciado en {command.path}. Los resultados aparecerán pronto.", "path": command.path}

@router.get("/duplicates")
async def get_found_duplicates():
    """Obtiene la lista de duplicados encontrados por el Bot Organizador."""
    logger.info("Acceso al endpoint de duplicados encontrados.")
    duplicates_json = get_bot_state(bot_name="Bot Organizer", state_key="organizer_duplicates_found")
    if not duplicates_json:
        logger.info("No hay duplicados encontrados todavía.")
        return []
    return duplicates_json

@router.post("/delete_duplicates")
async def delete_approved_duplicates(command: DeleteDuplicatesCommand):
    """Envía una orden al Bot Organizador para eliminar los archivos duplicados aprobados."""
    logger.info(f"Comando recibido: Eliminar {len(command.files)} duplicados aprobados.")
    send_command(bot_name="Bot Organizer", command_type="delete_duplicates", payload={"files": command.files})
    return {"message": "Orden de eliminación de duplicados enviada.", "files_count": len(command.files)}
