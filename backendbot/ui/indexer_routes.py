import os

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.backendbot.utils.logging_config import logger

router = APIRouter(
    prefix="/api/v1/indexer",
    tags=["Indexer"],
)


class IndexCommand(BaseModel):
    path: str


# Almacenamiento local simple para índice de archivos
file_index = []


@router.post("/start_indexing")
async def start_indexing_path(command: IndexCommand):
    """Inicia la indexación de archivos en la ruta especificada."""
    logger.info(f"Comando recibido: Iniciar indexación en {command.path}")
    if not os.path.exists(command.path):
        raise HTTPException(status_code=400, detail=f"Ruta no existe: {command.path}")

    # Simulación de indexación (en implementación real, esto activaría el bot)
    indexed_files = []
    for root, dirs, files in os.walk(command.path):
        for file in files:
            file_path = os.path.join(root, file)
            indexed_files.append(
                {
                    "filename": file,
                    "path": file_path,
                    "size": os.path.getsize(file_path),
                    "modified": os.path.getmtime(file_path),
                }
            )

    file_index.extend(indexed_files)
    logger.info(f"Indexación completada: {len(indexed_files)} archivos indexados.")

    return {
        "message": f"Indexación de {command.path} completada. {len(indexed_files)} archivos indexados.",
        "path": command.path,
    }


@router.get("/search")
async def search_files(query: str = Query(..., min_length=1)):
    """Busca archivos en el índice por palabra clave."""
    logger.info(f"Acceso al endpoint de búsqueda con query: {query}")
    search_terms = [term.lower() for term in query.split()]

    if not search_terms:
        return []

    # Búsqueda simple en el índice local
    results = []
    for file_data in file_index:
        filename_lower = file_data["filename"].lower()
        if any(term in filename_lower for term in search_terms):
            results.append(file_data)

    logger.info(f"Búsqueda completada. Encontrados {len(results)} resultados.")
    return results
