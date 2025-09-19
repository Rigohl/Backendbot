"""
BotManager - Coordinador simple de todos los bots de BackendBot
"""

import os
import sys
import psutil
from typing import Dict, Any

# Añadir path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.backendbot.core.di.container import container


class BaseBot:
    """Clase base para todos los bots"""

    def __init__(self, name: str):
        self.name = name
        self.logger = container.get_logger()
        self.config = container.get_config_manager()
        self.data_repo = container.get_data_repository()

    def execute(self, action: str) -> str:
        """Ejecutar acción en el bot"""
        raise NotImplementedError

    def get_status(self) -> str:
        """Obtener estado del bot"""
        return f"{self.name} operativo"

    def is_available(self) -> bool:
        """Verificar si el bot está disponible"""
        return True


class MonitorBot(BaseBot):
    """Bot Monitor - Monitorea recursos del sistema"""

    def __init__(self):
        super().__init__("Monitor")

    def execute(self, action: str) -> str:
        """Ejecutar acción del monitor"""
        if action == "status":
            # Obtener stats básicos del sistema
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory()
            return f"📊 CPU: {cpu}%, RAM: {ram.percent}%"
        elif action == "start":
            return "Monitor iniciado"
        else:
            return f"Acción '{action}' no reconocida para Monitor"


class OrganizerBot(BaseBot):
    """Bot Organizer - Organiza archivos y carpetas"""

    def __init__(self):
        super().__init__("Organizer")

    def execute(self, action: str) -> str:
        """Ejecutar acción del organizer"""
        if action == "status":
            return "Organizer listo para organizar"
        elif action == "scan":
            return "Escaneando archivos..."
        else:
            return f"Acción '{action}' no reconocida para Organizer"


class IndexerBot(BaseBot):
    """Bot Indexer - Indexa y busca archivos"""

    def __init__(self):
        super().__init__("Indexer")

    def execute(self, action: str) -> str:
        """Ejecutar acción del indexer"""
        if action == "status":
            return "Indexer listo para buscar"
        elif action.startswith("search"):
            query = action.replace("search", "").strip()
            return f"Buscando '{query}'..."
        else:
            return f"Acción '{action}' no reconocida para Indexer"


class GuardianBot(BaseBot):
    """Bot Guardian - Supervisa y protege"""

    def __init__(self):
        super().__init__("Guardian")

    def execute(self, action: str) -> str:
        """Ejecutar acción del guardian"""
        if action == "status":
            return "Guardian vigilando"
        elif action == "backup":
            return "Creando backup..."
        else:
            return f"Acción '{action}' no reconocida para Guardian"


class OptimizerBot(BaseBot):
    """Bot Optimizer - Optimiza rendimiento"""

    def __init__(self):
        super().__init__("Optimizer")

    def execute(self, action: str) -> str:
        """Ejecutar acción del optimizer"""
        if action == "status":
            return "Optimizer listo"
        elif action == "clean":
            return "Limpiando sistema..."
        else:
            return f"Acción '{action}' no reconocida para Optimizer"


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
            'optimizer': OptimizerBot()
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
  optimizer [acción]- Bot Optimizador (rendimiento, limpieza)

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