import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.backendbot.utils.logging_config import logger

router = APIRouter(
    prefix="/api/v1/organizer",
    tags=["Organizer"],
)


class ScanCommand(BaseModel):
    path: str


class DeleteDuplicatesCommand(BaseModel):
    files: list[str]


# Almacenamiento local simple para estado del bot
bot_state = {"organizer_duplicates_found": []}


@router.post("/scan")
async def start_scan_duplicates(command: ScanCommand):
    """Inicia un escaneo de duplicados en la ruta especificada."""
    logger.info(f"Comando recibido: Iniciar escaneo de duplicados en {command.path}")
    if not os.path.exists(command.path):
        raise HTTPException(status_code=400, detail=f"Ruta no existe: {command.path}")

    # Simulación de escaneo (en implementación real, esto activaría el bot)
    duplicates = []  # Placeholder
    bot_state["organizer_duplicates_found"] = duplicates

    return {
        "message": f"Escaneo de duplicados iniciado en {command.path}. Los resultados aparecerán pronto.",
        "path": command.path,
    }


@router.get("/duplicates")
async def get_found_duplicates():
    """Obtiene la lista de duplicados encontrados por el Bot Organizador."""
    logger.info("Acceso al endpoint de duplicados encontrados.")
    duplicates = bot_state.get("organizer_duplicates_found", [])
    if not duplicates:
        logger.info("No hay duplicados encontrados todavía.")
        return []
    return duplicates


@router.post("/delete_duplicates")
async def delete_approved_duplicates(command: DeleteDuplicatesCommand):
    """Envía una orden al Bot Organizador para eliminar los archivos duplicados aprobados."""
    logger.info(
        f"Comando recibido: Eliminar {len(command.files)} duplicados aprobados."
    )

    # Simulación de eliminación (en implementación real, esto activaría el bot)
    deleted_count = 0
    for file_path in command.files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted_count += 1
                logger.info(f"Archivo eliminado: {file_path}")
            except Exception as e:
                logger.error(f"Error eliminando {file_path}: {e}")

    return {
        "message": f"Eliminados {deleted_count} de {len(command.files)} archivos.",
        "files_count": deleted_count,
    }
