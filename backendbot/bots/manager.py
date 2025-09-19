"""BotManager - Coordinador simple de todos los bots de BackendBot."""

import os
import psutil
import json
import datetime
import threading
import time
import schedule
from typing import Dict, List, Callable

from backendbot.core.di.container import container
from backendbot.core.database.models import BotRun
from .auditor_files import AuditorFilesBot
from .auditor_programs import AuditorProgramsBot
from .chat import ChatBot
from .guardian import GuardianBot
from .indexer import IndexerBot
from .monitor import MonitorBot
from .organizer import OrganizerBot

# Importar bots individuales



class BotManager:
    """Coordinador de bots - gestiona todos los bots especializados.

    Implementado como singleton para evitar múltiples instancias en diferentes
    puntos de la aplicación (por ejemplo UI + orquestador) que produzcan
    conteos duplicados de bots.
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self.__class__._initialized:
            return

        self.logger = container.get_logger()
        self.config = container.get_config_manager()
        self.data_repo = container.get_data_repository()
        self.db_manager = container.get_db_manager()

        self.bots = {}
        self._load_bots()

        # Sistema de operación autónoma
        self.autonomous_mode = False
        self.monitoring_thread = None
        self.scheduler_thread = None
        self.stop_event = threading.Event()

        self.__class__._initialized = True

    def _load_bots(self):
        """Cargar todos los bots disponibles."""
        # Instanciar únicamente los bots canónicos para la API pública.
        # Evita incluir bots auxiliares/experimentales que inflen el conteo.
        # Registrar mediante el método `register_bot` para evitar duplicados.
        canonical = {
            "monitor": MonitorBot,
            "organizer": OrganizerBot,
            "indexer": IndexerBot,
            "guardian": GuardianBot,
            "chat": ChatBot,
        }

        for key, cls in canonical.items():
            try:
                instance = cls()
                self.register_bot(key, instance)
            except Exception as e:
                # No bloquear la carga completa por fallo de un bot
                try:
                    self.logger.error(f"Error cargando bot '{key}': {e}")
                except Exception:
                    pass
        # Posibilidad de incluir bots adicionales (auditores, chat, etc.)
        include_extras = os.environ.get("BACKENDBOT_INCLUDE_EXTRA_BOTS", "0").lower() in ("1", "true", "yes")
        try:
            # Preferir configuración explícita del config manager si existe
            cfg = None
            if hasattr(self.config, "get_settings"):
                cfg = self.config.get_settings()
            elif isinstance(self.config, dict):
                cfg = self.config

            if isinstance(cfg, dict):
                bots_cfg = cfg.get("bots", {})
                if "include_extras" in bots_cfg:
                    include_extras = bool(bots_cfg.get("include_extras"))
        except Exception:
            pass

        if include_extras:
            extras = {
                "auditor_files": AuditorFilesBot,
                "auditor_programs": AuditorProgramsBot,
                "chat": ChatBot,
            }
            for key, cls in extras.items():
                try:
                    instance = cls()
                    self.register_bot(key, instance)
                except Exception as e:
                    try:
                        self.logger.error(f"Error cargando bot extra '{key}': {e}")
                    except Exception:
                        pass

        # Registrar resumen
        try:
            self.logger.info(f"✅ Cargados {len(self.bots)} bots exitosamente")
        except Exception:
            # Logger puede no estar completamente inicializado en entornos de test
            pass

    def enable_extra_bots(self):
        """Habilitar e instanciar bots adicionales en tiempo de ejecución.

        Esto puede usarse desde scripts o durante el inicio si se desea activar
        los bots 'extra' sin reiniciar la aplicación.
        """
        try:
            # Reusar la lógica de inclusión usando variables de entorno temporal
            os.environ["BACKENDBOT_INCLUDE_EXTRA_BOTS"] = "1"
            # Ejecutar carga de bots adicionales
            self._load_bots()
        except Exception:
            try:
                self.logger.error("No se pudieron habilitar bots adicionales")
            except Exception:
                pass

    def disable_extra_bots(self):
        """Deshabilitar (remover) bots adicionales si están presentes.

        Esto elimina del registro los bots marcados como 'extra' y deja sólo
        los bots canónicos cargados inicialmente.
        """
        extras_keys = ["auditor_files", "auditor_programs", "chat"]
        removed = []
        for key in extras_keys:
            if key in self.bots:
                try:
                    bot = self.bots.pop(key)
                    # Intentar detener el bot si tiene stop()
                    if hasattr(bot, "stop") and callable(bot.stop):
                        try:
                            bot.stop()
                        except Exception:
                            pass
                    removed.append(key)
                except Exception:
                    pass

        try:
            self.logger.info(f"Bots extras removidos: {removed}")
        except Exception:
            pass
        return removed

    def register_bot(self, key: str, instance) -> bool:
        """Registrar un bot de forma segura evitando duplicados.

        Args:
            key: clave identificadora corta del bot (ej. 'monitor')
            instance: instancia del bot

        Returns:
            True si el bot fue registrado, False si ya existía.
        """
        if not key:
            return False

        if key in self.bots:
            try:
                self.logger.warning(f"Intento de registro duplicado para bot '{key}'")
            except Exception:
                pass
            return False

        self.bots[key] = instance
        return True

    def process_command(self, command: str) -> str:
        """Procesar comando del usuario y delegar al bot apropiado.

        Args:
        ----
            command: Comando del usuario

        Returns:
        -------
            Respuesta del bot
        """
        command = command.strip().lower()

        # Comandos básicos del sistema
        if command in ["help", "ayuda", "?"]:
            return self._get_help()

        if command in ["status", "estado"]:
            return self._get_status()

        # Comandos de modo autónomo
        if command in ["autonomous start", "autonomo iniciar", "modo autonomo"]:
            return self.start_autonomous_mode()

        if command in ["autonomous stop", "autonomo detener", "parar autonomo"]:
            return self.stop_autonomous_mode()

        if command in ["autonomous status", "estado autonomo"]:
            status = self.get_autonomous_status()
            return f"""🤖 Estado del Modo Autónomo:

Activo: {'✅ Sí' if status['active'] else '❌ No'}
Thread Monitoreo: {'✅ Vivo' if status['monitoring_thread_alive'] else '❌ Muerto'}
Thread Programado: {'✅ Vivo' if status['scheduler_thread_alive'] else '❌ Muerto'}

Próximas tareas programadas:
""" + "\n".join([
                f"• {task['job']} - {task['next_run'] or 'Pendiente'}"
                for task in status['next_scheduled_tasks'][:5]  # Mostrar solo las primeras 5
            ])

        # Delegar a bots específicos
        if command.startswith("monitor"):
            return self._process_bot_command("monitor", command)

        elif command.startswith("organizer") or command.startswith("organizar"):
            return self._process_bot_command("organizer", command)

        elif command.startswith("indexer") or command.startswith("indexar"):
            return self._process_bot_command("indexer", command)

        elif command.startswith("guardian") or command.startswith("guardar"):
            return self._process_bot_command("guardian", command)

        elif command.startswith("optimizer") or command.startswith("optimizar"):
            return self._process_bot_command("optimizer", command)

        elif command.startswith("auditor_files") or command.startswith(
            "auditor_archivos"
        ):
            return self._process_bot_command("auditor_files", command)

        elif command.startswith("auditor_programs") or command.startswith(
            "auditor_programas"
        ):
            return self._process_bot_command("auditor_programs", command)

        elif command.startswith("chat"):
            return self._process_bot_command("chat", command)

        else:
            # Usar ChatBot para interpretar lenguaje natural
            chat_command = f"chat {command}"
            return self._process_bot_command("chat", chat_command)

    def _process_bot_command(self, bot_name: str, command: str) -> str:
        """Procesar comando específico para un bot."""
        if bot_name not in self.bots:
            return f"Bot '{bot_name}' no disponible."

        # Temporalmente deshabilitar logging en DB para evitar errores
        try:
            # Extraer parámetros del comando
            parts = command.split()
            if len(parts) > 1:
                action = " ".join(parts[1:])
            else:
                action = "status"  # Por defecto mostrar estado

            # Ejecutar acción en el bot
            result = self.bots[bot_name].execute(action)
            return result

        except Exception as e:
            error_msg = f"Error ejecutando comando en {bot_name}: {str(e)}"
            try:
                self.logger.error(error_msg)
            except Exception:
                pass
            return error_msg

    def _log_bot_run_start(self, bot_name, command):
        with self.db_manager.get_db() as db:
            run = BotRun(
                bot_name=bot_name,
                start_time=datetime.datetime.utcnow(),
                status="running",
                result=json.dumps({"command": command})
            )
            db.add(run)
            db.commit()
            db.refresh(run)
            return run

    def _log_bot_run_end(self, run_record, status, result):
        with self.db_manager.get_db() as db:
            run_record.end_time = datetime.datetime.utcnow()
            run_record.status = status
            run_record.result = json.dumps(result)
            db.add(run_record)
            db.commit()

    def _get_help(self) -> str:
        """Obtener ayuda general."""
        return """
🤖 BackendBot - Comandos disponibles:

📊 SISTEMA:
  help/ayuda/?     - Mostrar esta ayuda
  status/estado    - Estado general del sistema

🤖 MODO AUTÓNOMO:
  autonomous start/modo autonomo     - Iniciar monitoreo autónomo
  autonomous stop/parar autonomo     - Detener modo autónomo
  autonomous status/estado autonomo  - Estado del modo autónomo

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

    def _get_status(self) -> str:
        """Obtener estado general del sistema."""
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
        """Obtener instancia de un bot específico."""
        return self.bots.get(name)

    def start_all_bots(self):
        """Iniciar todos los bots."""
        for bot in self.bots.values():
            if hasattr(bot, 'start') and callable(bot.start):
                bot.start()

    def stop_all_bots(self):
        """Detener todos los bots."""
        for bot in self.bots.values():
            if hasattr(bot, 'stop') and callable(bot.stop):
                bot.stop()

    def get_all_bot_status(self):
        """Obtener el estado de todos los bots."""
        statuses = {}
        for name, bot in self.bots.items():
            if hasattr(bot, 'get_status') and callable(bot.get_status):
                statuses[name] = bot.get_status()
        return statuses

    # ===== SISTEMA DE OPERACIÓN AUTÓNOMA =====

    def start_autonomous_mode(self) -> str:
        """Iniciar modo autónomo con monitoreo continuo y tareas programadas."""
        if self.autonomous_mode:
            return "⚠️ El modo autónomo ya está activo"

        try:
            self.autonomous_mode = True
            self.stop_event.clear()

            # Iniciar thread de monitoreo continuo
            self.monitoring_thread = threading.Thread(
                target=self._autonomous_monitoring_loop,
                daemon=True,
                name="AutonomousMonitor"
            )
            self.monitoring_thread.start()

            # Iniciar thread de tareas programadas
            self.scheduler_thread = threading.Thread(
                target=self._scheduled_tasks_loop,
                daemon=True,
                name="ScheduledTasks"
            )
            self.scheduler_thread.start()

            # Configurar tareas programadas
            self._setup_scheduled_tasks()

            self.logger.info("🚀 Modo autónomo iniciado", "BotManager")
            return "✅ Modo autónomo activado - Monitoreo continuo y tareas programadas iniciadas"

        except Exception as e:
            self.autonomous_mode = False
            try:
                self.logger.error(f"Error iniciando modo autónomo: {e}")
            except Exception:
                pass
            return f"❌ Error iniciando modo autónomo: {str(e)}"

    def stop_autonomous_mode(self) -> str:
        """Detener modo autónomo."""
        if not self.autonomous_mode:
            return "⚠️ El modo autónomo no está activo"

        try:
            self.autonomous_mode = False
            self.stop_event.set()

            # Esperar a que los threads terminen
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)

            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)

            self.logger.info("⏹️ Modo autónomo detenido", "BotManager")
            return "✅ Modo autónomo detenido"

        except Exception as e:
            try:
                self.logger.error(f"Error deteniendo modo autónomo: {e}")
            except Exception:
                pass
            return f"❌ Error deteniendo modo autónomo: {str(e)}"

    def _autonomous_monitoring_loop(self):
        """Loop de monitoreo autónomo que se ejecuta en background."""
        self.logger.info("🔄 Iniciando loop de monitoreo autónomo", "BotManager")

        while not self.stop_event.is_set() and self.autonomous_mode:
            try:
                # Monitoreo básico del sistema cada 30 segundos
                self._perform_autonomous_monitoring()

                # Verificar alertas cada 30 segundos
                self._check_autonomous_alerts()

                # Dormir 30 segundos
                self.stop_event.wait(30)

            except Exception as e:
                try:
                    self.logger.error(f"Error en loop de monitoreo autónomo: {e}")
                except Exception:
                    pass
                self.stop_event.wait(60)  # Esperar más tiempo si hay error

    def _scheduled_tasks_loop(self):
        """Loop de tareas programadas que se ejecuta en background."""
        self.logger.info("📅 Iniciando loop de tareas programadas", "BotManager")

        while not self.stop_event.is_set() and self.autonomous_mode:
            try:
                # Ejecutar tareas programadas pendientes
                schedule.run_pending()
                self.stop_event.wait(60)  # Revisar cada minuto

            except Exception as e:
                try:
                    self.logger.error(f"Error en loop de tareas programadas: {e}")
                except Exception:
                    pass
                self.stop_event.wait(120)  # Esperar más tiempo si hay error

    def _setup_scheduled_tasks(self):
        """Configurar tareas programadas para operación autónoma."""
        # Limpiar tareas anteriores
        schedule.clear()

        # Tarea de mantenimiento diario (a las 2 AM)
        schedule.every().day.at("02:00").do(self._daily_maintenance)

        # Optimización semanal (domingos a las 3 AM)
        schedule.every().sunday.at("03:00").do(self._weekly_optimization)

        # Verificación de seguridad cada 6 horas
        schedule.every(6).hours.do(self._security_check)

        # Backup semanal (sábados a las 4 AM)
        schedule.every().saturday.at("04:00").do(self._weekly_backup)

        self.logger.info("📅 Tareas programadas configuradas", "BotManager")

    def _perform_autonomous_monitoring(self):
        """Realizar monitoreo autónomo básico."""
        try:
            # Obtener métricas del sistema
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Guardar en repositorio de datos si excede umbrales
            if cpu > 80 or memory.percent > 80 or disk.percent > 90:
                self.data_repo.save_system_event(
                    level="WARNING",
                    source="AutonomousMonitor",
                    message=f"Recursos altos - CPU: {cpu}%, RAM: {memory.percent}%, Disco: {disk.percent}%",
                    details={"cpu": cpu, "memory": memory.percent, "disk": disk.percent}
                )

        except Exception as e:
            try:
                self.logger.error(f"Error en monitoreo autónomo: {e}")
            except Exception:
                pass

    def _check_autonomous_alerts(self):
        """Verificar alertas autónomas."""
        try:
            # Verificar procesos problemáticos
            problematic_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if proc.info['cpu_percent'] > 90 or proc.info['memory_percent'] > 80:
                        problematic_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if problematic_processes:
                self.data_repo.save_system_event(
                    level="WARNING",
                    source="AutonomousAlerts",
                    message=f"Procesos problemáticos detectados: {len(problematic_processes)}",
                    details={"processes": problematic_processes}
                )

        except Exception as e:
            try:
                self.logger.error(f"Error verificando alertas autónomas: {e}")
            except Exception:
                pass

    def _daily_maintenance(self):
        """Tarea de mantenimiento diario."""
        try:
            self.logger.info("🛠️ Ejecutando mantenimiento diario", "BotManager")

            # Ejecutar optimización del sistema
            if 'optimizer' in self.bots:
                result = self.bots['optimizer'].execute("optimize")
                self.logger.info(f"Optimización diaria completada: {result}", "BotManager")

            # Verificar y organizar archivos
            if 'organizer' in self.bots:
                result = self.bots['organizer'].execute("scan")
                self.logger.info(f"Escaneo de archivos completado: {result}", "BotManager")

        except Exception as e:
            try:
                self.logger.error(f"Error en mantenimiento diario: {e}")
            except Exception:
                pass

    def _weekly_optimization(self):
        """Optimización semanal completa."""
        try:
            self.logger.info("🔧 Ejecutando optimización semanal", "BotManager")

            # Optimización profunda del sistema
            if 'optimizer' in self.bots:
                result = self.bots['optimizer'].execute("deep_clean")
                self.logger.info(f"Optimización semanal completada: {result}", "BotManager")

            # Verificación completa de archivos
            if 'auditor_files' in self.bots:
                result = self.bots['auditor_files'].execute("full_scan")
                self.logger.info(f"Auditoría de archivos completada: {result}", "BotManager")

        except Exception as e:
            try:
                self.logger.error(f"Error en optimización semanal: {e}")
            except Exception:
                pass

    def _security_check(self):
        """Verificación de seguridad programada."""
        try:
            self.logger.info("🔒 Ejecutando verificación de seguridad", "BotManager")

            if 'guardian' in self.bots:
                result = self.bots['guardian'].execute("security_scan")
                self.logger.info(f"Verificación de seguridad completada: {result}", "BotManager")

        except Exception as e:
            try:
                self.logger.error(f"Error en verificación de seguridad: {e}")
            except Exception:
                pass

    def _weekly_backup(self):
        """Backup semanal."""
        try:
            self.logger.info("💾 Ejecutando backup semanal", "BotManager")

            if 'guardian' in self.bots:
                result = self.bots['guardian'].execute("backup")
                self.logger.info(f"Backup semanal completado: {result}", "BotManager")

        except Exception as e:
            try:
                self.logger.error(f"Error en backup semanal: {e}")
            except Exception:
                pass

    def get_autonomous_status(self) -> dict:
        """Obtener estado del modo autónomo."""
        return {
            "active": self.autonomous_mode,
            "monitoring_thread_alive": self.monitoring_thread.is_alive() if self.monitoring_thread else False,
            "scheduler_thread_alive": self.scheduler_thread.is_alive() if self.scheduler_thread else False,
            "next_scheduled_tasks": [
                {
                    "job": str(job),
                    "next_run": job.next_run.isoformat() if job.next_run else None
                }
                for job in schedule.jobs
            ]
        }
