import time
import subprocess
import sys
import os
from backendbot.utils.logging_config import logger

# Lista de bots que el guardián debe supervisar.
# Cada bot es una tupla con su nombre (para logging) y la ruta al script.
BOTS_TO_MANAGE = [
    ("Bot Monitor", [sys.executable, "-m", "backendbot.bots.bot_monitor"]),
    ("Bot Organizer", [sys.executable, "-m", "backendbot.bots.bot_organizer"]),
    ("Bot Indexer", [sys.executable, "-m", "backendbot.bots.bot_indexer"]),
]

def guardian_worker():
    """Worker que supervisa y reinicia otros bots si fallan."""
    logger.info("🛡️ Bot Guardián: Iniciando... Supervisando a los trabajadores.")
    bot_processes = {}

    # Iniciar todos los bots por primera vez
    for bot_name, bot_command in BOTS_TO_MANAGE:
        logger.info(f"🛡️ Bot Guardián: Iniciando {bot_name}...")
        bot_processes[bot_name] = subprocess.Popen(bot_command)

    # Bucle de supervisión
    while True:
        time.sleep(10) # Verificar cada 10 segundos
        for bot_name, bot_command in BOTS_TO_MANAGE:
            process = bot_processes.get(bot_name)
            if process is None or process.poll() is not None: # Si el proceso no existe o ha terminado
                logger.warning(f"🛡️ Bot Guardián: ¡Alerta! {bot_name} se ha caído. Reiniciando...")
                bot_processes[bot_name] = subprocess.Popen(bot_command)

if __name__ == "__main__":
    guardian_worker()
