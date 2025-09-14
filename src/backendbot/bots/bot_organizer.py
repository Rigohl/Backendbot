import asyncio
import json
import hashlib
import os
import send2trash
from src.backendbot.utils.logging_config import logger
from src.backendbot.utils.db_logger import log_system_event, log_bot_action
from src.backendbot.utils.db_messaging import get_pending_command, complete_command, set_bot_state, send_result

BOT_NAME = "Bot Organizer"
ORGANIZER_DUPLICATES_KEY = "organizer_duplicates_found"

async def calculate_file_hash(filepath, hash_algo=hashlib.md5, chunk_size=4096):
    """Calcula el hash de un archivo."""
    hasher = hash_algo()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error al calcular hash de {filepath}: {e}")
        log_system_event(level="ERROR", source=BOT_NAME, message=f"Error al calcular hash de {filepath}", details=str(e))
        return None

async def find_duplicates(path_to_scan):
    """Encuentra archivos duplicados en el path dado."""
    logger.info(f"🤖 {BOT_NAME}: Escaneando '{path_to_scan}' en busca de duplicados...")
    log_bot_action(bot_name=BOT_NAME, action_type="scan_duplicates", status="started", target=path_to_scan)
    hashes = {}
    duplicates = []
    for dirpath, _, filenames in os.walk(path_to_scan):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.islink(filepath):
                logger.debug(f"Saltando enlace simbólico: {filepath}")
                continue
            file_hash = await calculate_file_hash(filepath)
            if file_hash is None: # Hash calculation failed
                continue

            if file_hash in hashes:
                # Check if this duplicate group already exists
                found_in_duplicates = False
                for dup_group in duplicates:
                    if dup_group["hash"] == file_hash:
                        if filepath not in dup_group["paths"]:
                            dup_group["paths"].append(filepath)
                        found_in_duplicates = True
                        break
                if not found_in_duplicates:
                    # This means it's a new group of duplicates
                    duplicates.append({"hash": file_hash, "paths": [hashes[file_hash], filepath]})
            else:
                hashes[file_hash] = filepath
    logger.info(f"🤖 {BOT_NAME}: Escaneo completado. Encontrados {len(duplicates)} grupos de duplicados.")
    log_bot_action(bot_name=BOT_NAME, action_type="scan_duplicates", status="completed", target=path_to_scan, result=json.dumps({"count": len(duplicates)}))
    return duplicates

async def organizer_worker():
    """Worker que escucha comandos de organización y ejecuta tareas."""
    logger.info(f"🤖 {BOT_NAME}: Iniciando...")
    log_system_event(level="INFO", source=BOT_NAME, message=f"{BOT_NAME} iniciado.")

    while True:
        try:
            command = get_pending_command(BOT_NAME)
            if command:
                command_payload = json.loads(command.payload)
                logger.info(f"🤖 {BOT_NAME}: Comando recibido: {command_payload}")

                if command.command_type == 'scan_duplicates':
                    path = command_payload['path']
                    duplicates = await find_duplicates(path)
                    set_bot_state(bot_name=BOT_NAME, state_key=ORGANIZER_DUPLICATES_KEY, state_value=duplicates)
                    send_result(bot_name=BOT_NAME, result_type="scan_duplicates_result", payload={
                        "command_id": command.id,
                        "count": len(duplicates),
                        "path": path
                    })
                    complete_command(command.id)
                elif command.command_type == 'delete_duplicates':
                    files_to_delete = command_payload['files']
                    deleted_count = 0
                    log_bot_action(bot_name=BOT_NAME, action_type="delete_duplicates", status="started", target=json.dumps(files_to_delete))
                    for filepath in files_to_delete:
                        try:
                            send2trash.send2trash(filepath) # Usar send2trash en lugar de os.remove
                            deleted_count += 1
                            logger.info(f"🤖 {BOT_NAME}: Enviado a papelera: {filepath}")
                        except Exception as e:
                            logger.error(f"🤖 {BOT_NAME}: Error al enviar a papelera {filepath}: {e}")
                            log_system_event(level="ERROR", source=BOT_NAME, message=f"Error al enviar a papelera {filepath}", details=str(e))
                    send_result(bot_name=BOT_NAME, result_type="delete_duplicates_result", payload={
                        "command_id": command.id,
                        "deleted_count": deleted_count
                    })
                    complete_command(command.id)

            await asyncio.sleep(1) # Pequeña pausa para no saturar el CPU

        except Exception as e:
            logger.error(f"🤖 {BOT_NAME}: Error - {e}. Reintentando en 5 segundos...")
            log_system_event(level="ERROR", source=BOT_NAME, message=f"Error en bucle principal: {e}", details=str(e))
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(organizer_worker())
