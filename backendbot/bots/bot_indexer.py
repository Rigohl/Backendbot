import asyncio
import json
import os
import time

from src.backendbot.utils.db_logger import log_bot_action, log_system_event
from src.backendbot.utils.db_messaging import (complete_command,
                                               get_pending_command,
                                               send_result, set_bot_state)
from src.backendbot.utils.logging_config import logger

BOT_NAME = "Bot Indexer"
INDEXER_FILE_PREFIX = "indexed_file:"


async def index_file(filepath):
    """Indexa un archivo en la DB."""
    try:
        stat = os.stat(filepath)
        file_id = f"{filepath}_{stat.st_mtime}"  # Simple ID based on path and modification time

        file_data = {
            "path": filepath,
            "filename": os.path.basename(filepath),
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "indexed_at": time.time(),
        }
        set_bot_state(
            bot_name=BOT_NAME,
            state_key=f"{INDEXER_FILE_PREFIX}{file_id}",
            state_value=file_data,
        )

        logger.info(f"🤖 {BOT_NAME}: Indexado {filepath}")
    except Exception as e:
        logger.error(f"🤖 {BOT_NAME}: Error al indexar {filepath}: {e}")
        log_system_event(
            level="ERROR",
            source=BOT_NAME,
            message=f"Error al indexar {filepath}",
            details=str(e),
        )


async def scan_and_index_path(path_to_scan):
    """Escanea una ruta y indexa sus archivos."""
    logger.info(f"🤖 {BOT_NAME}: Escaneando y indexando '{path_to_scan}'...")
    log_bot_action(
        bot_name=BOT_NAME,
        action_type="start_indexing",
        status="started",
        target=path_to_scan,
    )
    indexed_count = 0
    for dirpath, _, filenames in os.walk(path_to_scan):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.islink(filepath):
                logger.debug(f"Saltando enlace simbólico: {filepath}")
                continue
            await index_file(filepath)
            indexed_count += 1
    logger.info(
        f"🤖 {BOT_NAME}: Escaneo e indexación completados. {indexed_count} archivos indexados."
    )
    log_bot_action(
        bot_name=BOT_NAME,
        action_type="start_indexing",
        status="completed",
        target=path_to_scan,
        result=json.dumps({"indexed_count": indexed_count}),
    )
    return indexed_count


async def indexer_worker():
    """Worker que escucha comandos de indexación y ejecuta tareas."""
    logger.info(f"🤖 {BOT_NAME}: Iniciando...")
    log_system_event(level="INFO", source=BOT_NAME, message=f"{BOT_NAME} iniciado.")

    while True:
        try:
            command = get_pending_command(BOT_NAME)
            if command:
                command_payload = json.loads(command.payload)
                logger.info(f"🤖 {BOT_NAME}: Comando recibido: {command_payload}")

                if command.command_type == "start_indexing":
                    path = command_payload["path"]
                    indexed_count = await scan_and_index_path(path)
                    send_result(
                        bot_name=BOT_NAME,
                        result_type="indexed_count_result",
                        payload={
                            "command_id": command.id,
                            "indexed_count": indexed_count,
                            "path": path,
                        },
                    )
                    complete_command(command.id)

            await asyncio.sleep(1)  # Pequeña pausa para no saturar el CPU

        except Exception as e:
            logger.error(f"🤖 {BOT_NAME}: Error - {e}. Reintentando en 5 segundos...")
            log_system_event(
                level="ERROR",
                source=BOT_NAME,
                message=f"Error en bucle principal: {e}",
                details=str(e),
            )
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(indexer_worker())
