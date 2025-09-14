from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
import json

from src.backendbot.utils.logging_config import logger
from src.backendbot.utils.db_messaging import send_command, get_db_session, BotState
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/v1/indexer",
    tags=["Indexer"],
)

class IndexCommand(BaseModel):
    path: str

@router.post("/start_indexing")
async def start_indexing_path(command: IndexCommand):
    """Inicia la indexación de archivos en la ruta especificada."""
    logger.info(f"Comando recibido: Iniciar indexación en {command.path}")
    send_command(bot_name="Bot Indexer", command_type="start_indexing", payload={"path": command.path})
    return {"message": f"Indexación de {command.path} iniciada. Los resultados aparecerán pronto.", "path": command.path}

@router.get("/search")
async def search_files(query: str = Query(..., min_length=1), db: Session = Depends(get_db_session)):
    """Busca archivos en el índice por palabra clave."""
    logger.info(f"Acceso al endpoint de búsqueda con query: {query}")
    search_terms = [term.lower() for term in query.split()]
    
    if not search_terms:
        return []

    # Query BotState table for indexed files
    # This is a simplified search. A real search engine would be more complex.
    results = []
    for term in search_terms:
        # Search in state_value (JSON string) for the term
        # This is inefficient for large datasets, but works for basic demo
        files = db.query(BotState).filter(
            BotState.bot_name == "Bot Indexer",
            BotState.state_key.like(f"indexed_file:%"),
            BotState.state_value.ilike(f'%"filename": "%s%%"%' % term) # Case-insensitive search in filename
        ).all()
        for file_state in files:
            try:
                file_data = json.loads(file_state.state_value)
                results.append(file_data)
            except json.JSONDecodeError:
                logger.error(f"Error decodificando JSON de estado de archivo: {file_state.state_value}")
    
    # Remove duplicates from results if any
    unique_results = []
    seen_paths = set()
    for res in results:
        if res.get("path") and res["path"] not in seen_paths:
            unique_results.append(res)
            seen_paths.add(res["path"])

    logger.info(f"Búsqueda completada. Encontrados {len(unique_results)} resultados.")
    return unique_results
