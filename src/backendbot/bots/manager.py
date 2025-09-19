"""
BotManager - Coordinador simple de todos los bots de BackendBot
"""

import os
import sys
import psutil
from typing import Dict, Any

# Añadir path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backendbot.core.di.container import container

# Importar bots individuales
from .monitor import MonitorBot
from .organizer import OrganizerBot
from .indexer import IndexerBot
from .guardian import GuardianBot
from .auditor_files import AuditorFilesBot
from .auditor_programs import AuditorProgramsBot


class BotManager:
    """Coordinador de bots - gestiona todos los bots especializados"""

    def __init__(self):
        self.logger = container.get_logger()
        self.config = container.get_config_manager()
        self.data_repo = container.get_data_repository()

        self.bots = {}
        self._load_bots()

    def _load_bots(self):
        """Cargar todos los bots disponibles"""
        # Instanciar bots
        self.bots = {
            'monitor': MonitorBot(),
            'organizer': OrganizerBot(),
            'indexer': IndexerBot(),
            'guardian': GuardianBot(),
            'auditor_files': AuditorFilesBot(),
            'auditor_programs': AuditorProgramsBot()
        }

        self.logger.info(f"✅ Cargados {len(self.bots)} bots exitosamente", "BotManager")

    def process_command(self, command: str) -> str:
        """
        Procesar comando del usuario y delegar al bot apropiado

        Args:
            command: Comando del usuario

        Returns:
            Respuesta del bot
        """
        command = command.strip().lower()

        # Comandos básicos del sistema
        if command in ['help', 'ayuda', '?']:
            return self._get_help()

        if command in ['status', 'estado']:
            return self._get_status()

        # Delegar a bots específicos
        if command.startswith('monitor'):
            return self._process_bot_command('monitor', command)

        elif command.startswith('organizer') or command.startswith('organizar'):
            return self._process_bot_command('organizer', command)

        elif command.startswith('indexer') or command.startswith('indexar'):
            return self._process_bot_command('indexer', command)

        elif command.startswith('guardian') or command.startswith('guardar'):
            return self._process_bot_command('guardian', command)

        elif command.startswith('optimizer') or command.startswith('optimizar'):
            return self._process_bot_command('optimizer', command)

        elif command.startswith('auditor_files') or command.startswith('auditor_archivos'):
            return self._process_bot_command('auditor_files', command)

        elif command.startswith('auditor_programs') or command.startswith('auditor_programas'):
            return self._process_bot_command('auditor_programs', command)

        elif command.startswith('auditor_programs') or command.startswith('auditor_programas'):
            return self._process_bot_command('auditor_programs', command)

        else:
            return "Comando no reconocido. Usa 'help' para ver comandos disponibles."

    def _process_bot_command(self, bot_name: str, command: str) -> str:
        """Procesar comando específico para un bot"""
        if bot_name not in self.bots:
            return f"Bot '{bot_name}' no disponible."

        try:
            # Extraer parámetros del comando
            parts = command.split()
            if len(parts) > 1:
                action = ' '.join(parts[1:])
            else:
                action = 'status'  # Por defecto mostrar estado

            # Ejecutar acción en el bot
            result = self.bots[bot_name].execute(action)

            # Guardar acción en el repositorio
            self.data_repo.save_bot_action(
                bot_name=bot_name,
                action_type=action,
                status="completed",
                target=command,
                result=result
            )

            return result

        except Exception as e:
            error_msg = f"Error ejecutando comando en {bot_name}: {str(e)}"
            self.logger.error(error_msg, "BotManager")

            # Guardar error en el repositorio
            self.data_repo.save_system_event(
                level="ERROR",
                source="BotManager",
                message=error_msg,
                details=str(e)
            )

            return error_msg

    def _get_help(self) -> str:
        """Obtener ayuda general"""
        help_text = """
🤖 BackendBot - Comandos disponibles:

📊 SISTEMA:
  help/ayuda/?     - Mostrar esta ayuda
  status/estado    - Estado general del sistema

🤖 BOTS ESPECIALIZADOS:
  monitor [acción]  - Bot Monitor (sistema, procesos)
  organizer [acción]- Bot Organizador (archivos, carpetas)
  indexer [acción]  - Bot Indexador (búsqueda, indexación)
  guardian [acción] - Bot Guardián (seguridad, backups)
    auditor_files [acción] - Bot Auditor de Archivos Antiguos
    auditor_programs [acción] - Bot Auditor de Programas

💡 Ejemplos:
  monitor status
  organizer scan
  indexer search documentos
  guardian backup
  optimizer clean

Cada bot tiene sus propios comandos. Usa 'bot status' para ver opciones específicas.
        """
        return help_text

    def _get_status(self) -> str:
        """Obtener estado general del sistema"""
        status = "📊 Estado de BackendBot:\n\n"

        # Estado de bots
        status += f"🤖 Bots cargados: {len(self.bots)}\n"
        for name, bot in self.bots.items():
            try:
                bot_status = bot.get_status()
                status += f"  ✅ {name}: {bot_status}\n"
            except:
                status += f"  ❌ {name}: Error\n"

        # Estado de memoria (simplificado)
        memory = psutil.virtual_memory()
        status += f"\n💾 Memoria: {memory.percent}% usada\n"

        return status

    def get_bot(self, name: str):
        """Obtener instancia de un bot específico"""
        return self.bots.get(name)