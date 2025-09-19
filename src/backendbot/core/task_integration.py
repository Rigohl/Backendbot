"""
Integración del Sistema de Tareas Programadas con los Bots
Conecta las tareas programadas con las funcionalidades de los bots existentes.
"""
from typing import Dict, Any, Callable
from pathlib import Path
import shutil
import os
from datetime import datetime
from src.backendbot.cron_jobs.task_scheduler import task_scheduler, TaskFrequency, TaskPriority
from src.backendbot.modes import mode_manager
from src.backendbot.modes.adaptive_learning import adaptive_learning
from src.backendbot.utils.logging_config import logger
from src.backendbot.utils.data_store import read_json, write_json, initialize_defaults

class TaskIntegration:
    def __init__(self):
        initialize_defaults()
        self.backup_dir = Path(".backendbot_data/backups")
        self.backup_dir.mkdir(exist_ok=True, parents=True)

        # Registrar tareas integradas
        self._register_integrated_tasks()

    def _register_integrated_tasks(self):
        """Registrar todas las tareas integradas con los bots"""

        # Tareas de limpieza y organización
        task_scheduler.add_task(
            task_id="cleanup_temp_files",
            name="Limpiar Archivos Temporales",
            function=self._cleanup_temp_files,
            frequency=TaskFrequency.DAILY,
            priority=TaskPriority.MEDIUM,
            conditions={'modes': ['editor', 'desarrollo', 'relax']}
        )

        task_scheduler.add_task(
            task_id="organize_files_auto",
            name="Organización Automática de Archivos",
            function=self._organize_files_auto,
            frequency=TaskFrequency.WEEKLY,
            priority=TaskPriority.HIGH,
            conditions={'modes': ['editor', 'desarrollo']}
        )

        # Tareas de monitoreo y optimización
        task_scheduler.add_task(
            task_id="system_health_check",
            name="Verificación de Salud del Sistema",
            function=self._system_health_check,
            frequency=TaskFrequency.HOURLY,
            priority=TaskPriority.LOW,
            conditions={'modes': ['editor', 'streaming', 'desarrollo', 'gaming']}
        )

        task_scheduler.add_task(
            task_id="performance_optimization",
            name="Optimización de Rendimiento",
            function=self._performance_optimization,
            frequency=TaskFrequency.DAILY,
            priority=TaskPriority.HIGH,
            conditions={'modes': ['editor', 'desarrollo']}
        )

        # Tareas de indexación y auditoría
        task_scheduler.add_task(
            task_id="update_file_index",
            name="Actualizar Índice de Archivos",
            function=self._update_file_index,
            frequency=TaskFrequency.DAILY,
            priority=TaskPriority.MEDIUM,
            conditions={'modes': ['editor', 'desarrollo']}
        )

        task_scheduler.add_task(
            task_id="audit_files_security",
            name="Auditoría de Seguridad de Archivos",
            function=self._audit_files_security,
            frequency=TaskFrequency.WEEKLY,
            priority=TaskPriority.CRITICAL,
            conditions={'modes': ['editor', 'desarrollo']}
        )

        # Tareas de backup y mantenimiento
        task_scheduler.add_task(
            task_id="backup_configurations",
            name="Backup de Configuraciones",
            function=self._backup_configurations,
            frequency=TaskFrequency.WEEKLY,
            priority=TaskPriority.CRITICAL,
            conditions={'modes': ['editor', 'desarrollo']}
        )

        task_scheduler.add_task(
            task_id="cleanup_logs",
            name="Limpieza de Logs Antiguos",
            function=self._cleanup_logs,
            frequency=TaskFrequency.MONTHLY,
            priority=TaskPriority.LOW,
            conditions={'modes': ['editor', 'desarrollo', 'relax']}
        )

        logger.info("Tareas integradas registradas exitosamente")

    # Funciones de tareas integradas

    def _cleanup_temp_files(self) -> str:
        """Limpiar archivos temporales del sistema"""
        try:
            temp_dirs = [
                Path("C:/Windows/Temp"),
                Path("C:/Users/DELL/AppData/Local/Temp"),
                Path("./temp"),
                Path("./__pycache__")
            ]

            cleaned_files = 0
            cleaned_size = 0

            for temp_dir in temp_dirs:
                if temp_dir.exists():
                    for file_path in temp_dir.rglob("*"):
                        if file_path.is_file():
                            try:
                                # Solo eliminar archivos antiguos (> 7 días)
                                if (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days > 7:
                                    size = file_path.stat().st_size
                                    file_path.unlink()
                                    cleaned_files += 1
                                    cleaned_size += size
                            except Exception as e:
                                logger.warning(f"No se pudo eliminar {file_path}: {e}")

            # Registrar en aprendizaje adaptativo
            adaptive_learning.record_user_action('cleanup', {
                'type': 'temp_files',
                'files_cleaned': cleaned_files,
                'size_cleaned': cleaned_size,
                'mode': mode_manager.get_mode_info()['mode']
            })

            return f"Limpieza completada: {cleaned_files} archivos eliminados, {cleaned_size / 1024 / 1024:.2f} MB liberados"

        except Exception as e:
            logger.error(f"Error en limpieza de archivos temporales: {e}")
            return f"Error en limpieza: {e}"

    def _organize_files_auto(self) -> str:
        """Organización automática de archivos"""
        try:
            # Aquí se integraría con BotOrganizerUI
            # Por simplicidad, organizamos archivos en el directorio actual
            workspace_dir = Path(".")
            organized_files = 0

            # Crear directorios de organización
            categories = {
                'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
                'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
                'videos': ['.mp4', '.avi', '.mkv', '.mov'],
                'music': ['.mp3', '.wav', '.flac'],
                'archives': ['.zip', '.rar', '.7z', '.tar.gz']
            }

            for category, extensions in categories.items():
                category_dir = workspace_dir / category
                category_dir.mkdir(exist_ok=True)

                for ext in extensions:
                    for file_path in workspace_dir.glob(f"*{ext}"):
                        if file_path.is_file() and not file_path.name.startswith('.'):
                            try:
                                shutil.move(str(file_path), str(category_dir / file_path.name))
                                organized_files += 1
                            except Exception as e:
                                logger.warning(f"No se pudo mover {file_path}: {e}")

            # Registrar en aprendizaje adaptativo
            adaptive_learning.record_user_action('organization', {
                'type': 'auto_organize',
                'files_organized': organized_files,
                'mode': mode_manager.get_mode_info()['mode']
            })

            return f"Organización completada: {organized_files} archivos organizados"

        except Exception as e:
            logger.error(f"Error en organización automática: {e}")
            return f"Error en organización: {e}"

    def _system_health_check(self) -> str:
        """Verificación de salud del sistema"""
        try:
            # Aquí se integraría con BotMonitorUI
            # Verificaciones básicas de salud
            health_issues = []

            # Verificar espacio en disco
            import psutil
            disk_usage = psutil.disk_usage('/')
            if disk_usage.percent > 90:
                health_issues.append(f"Espacio en disco bajo: {disk_usage.percent}%")

            # Verificar memoria
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                health_issues.append(f"Memoria alta: {memory.percent}%")

            # Verificar CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                health_issues.append(f"CPU alta: {cpu_percent}%")

            # Registrar en aprendizaje adaptativo
            adaptive_learning.record_user_action('health_check', {
                'issues_found': len(health_issues),
                'disk_usage': disk_usage.percent,
                'memory_usage': memory.percent,
                'cpu_usage': cpu_percent,
                'mode': mode_manager.get_mode_info()['mode']
            })

            if health_issues:
                return f"Problemas de salud detectados: {'; '.join(health_issues)}"
            else:
                return "Sistema saludable - No se detectaron problemas"

        except Exception as e:
            logger.error(f"Error en verificación de salud: {e}")
            return f"Error en verificación: {e}"

    def _performance_optimization(self) -> str:
        """Optimización de rendimiento del sistema"""
        try:
            # Aquí se integraría con BotOptimizerUI
            optimizations = []

            # Limpiar procesos innecesarios (simplificado)
            import psutil
            current_process = psutil.Process()
            children = current_process.children(recursive=True)

            terminated_processes = 0
            for child in children:
                try:
                    if child.name().lower() in ['notepad.exe', 'calc.exe']:  # Ejemplo
                        child.terminate()
                        terminated_processes += 1
                except:
                    pass

            if terminated_processes > 0:
                optimizations.append(f"{terminated_processes} procesos terminados")

            # Registrar en aprendizaje adaptativo
            adaptive_learning.record_user_action('optimization', {
                'type': 'performance',
                'optimizations_applied': len(optimizations),
                'mode': mode_manager.get_mode_info()['mode']
            })

            return f"Optimización completada: {'; '.join(optimizations) if optimizations else 'No se aplicaron optimizaciones'}"

        except Exception as e:
            logger.error(f"Error en optimización: {e}")
            return f"Error en optimización: {e}"

    def _update_file_index(self) -> str:
        """Actualizar índice de archivos"""
        try:
            # Aquí se integraría con BotIndexerUI
            indexed_files = 0
            index_file_name = 'file_index.json'

            # Indexar archivos en el workspace
            workspace_files = []
            for file_path in Path('.').rglob('*'):
                if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                    file_info = {
                        'path': str(file_path),
                        'name': file_path.name,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        'extension': file_path.suffix
                    }
                    workspace_files.append(file_info)
                    indexed_files += 1

            # Guardar índice mediante data_store
            write_json(index_file_name, {'files': workspace_files, 'last_updated': datetime.now().isoformat()})

            # Registrar en aprendizaje adaptativo
            adaptive_learning.record_user_action('indexing', {
                'files_indexed': indexed_files,
                'mode': mode_manager.get_mode_info()['mode']
            })

            return f"Índice actualizado: {indexed_files} archivos indexados"

        except Exception as e:
            logger.error(f"Error en actualización de índice: {e}")
            return f"Error en indexación: {e}"

    def _audit_files_security(self) -> str:
        """Auditoría de seguridad de archivos"""
        try:
            # Aquí se integraría con BotAuditorFilesUI
            security_issues = []
            audited_files = 0

            # Verificar archivos ejecutables en lugares no estándar
            suspicious_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif']
            safe_dirs = ['C:/Windows', 'C:/Program Files', 'C:/Program Files (x86)']

            for file_path in Path(".").rglob("*"):
                if file_path.is_file():
                    audited_files += 1
                    if file_path.suffix.lower() in suspicious_extensions:
                        if not any(str(file_path).startswith(safe_dir) for safe_dir in safe_dirs):
                            security_issues.append(f"Archivo ejecutable sospechoso: {file_path}")

            # Verificar archivos con permisos peligrosos
            for file_path in Path(".").rglob("*"):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        # Verificar si es ejecutable para todos
                        if stat.st_mode & 0o111:  # Ejecutable
                            security_issues.append(f"Archivo con permisos ejecutables: {file_path}")
                    except:
                        pass

            # Registrar en aprendizaje adaptativo
            adaptive_learning.record_user_action('audit', {
                'type': 'security',
                'files_audited': audited_files,
                'issues_found': len(security_issues),
                'mode': mode_manager.get_mode_info()['mode']
            })

            if security_issues:
                return f"Auditoría completada: {len(security_issues)} problemas de seguridad encontrados"
            else:
                return f"Auditoría completada: {audited_files} archivos auditados, sin problemas de seguridad"

        except Exception as e:
            logger.error(f"Error en auditoría de seguridad: {e}")
            return f"Error en auditoría: {e}"

    def _backup_configurations(self) -> str:
        """Backup de configuraciones importantes"""
        try:
            backup_files = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{timestamp}"

            backup_path.mkdir(exist_ok=True)

            # Archivos de configuración a respaldar
            config_files = [
                ".backendbot_data/scheduled_tasks.json",
                ".backendbot_data/adaptive_learning.json",
                ".backendbot_data/operation_modes.json",
                "config.py",
                "requirements.txt"
            ]

            for config_file in config_files:
                src_path = Path(config_file)
                if src_path.exists():
                    dst_path = backup_path / src_path.name
                    shutil.copy2(src_path, dst_path)
                    backup_files.append(src_path.name)

            # Registrar en aprendizaje adaptativo
            adaptive_learning.record_user_action('backup', {
                'type': 'configurations',
                'files_backed_up': len(backup_files),
                'backup_path': str(backup_path),
                'mode': mode_manager.get_mode_info()['mode']
            })

            return f"Backup completado: {len(backup_files)} archivos respaldados en {backup_path}"

        except Exception as e:
            logger.error(f"Error en backup: {e}")
            return f"Error en backup: {e}"

    def _cleanup_logs(self) -> str:
        """Limpieza de logs antiguos"""
        try:
            logs_dir = Path("logs")
            if not logs_dir.exists():
                return "No hay directorio de logs para limpiar"

            cleaned_files = 0
            total_size = 0

            # Eliminar logs más antiguos de 30 días
            for log_file in logs_dir.glob("*.log"):
                if (datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)).days > 30:
                    size = log_file.stat().st_size
                    log_file.unlink()
                    cleaned_files += 1
                    total_size += size

            # Registrar en aprendizaje adaptativo
            adaptive_learning.record_user_action('cleanup', {
                'type': 'old_logs',
                'files_cleaned': cleaned_files,
                'size_cleaned': total_size,
                'mode': mode_manager.get_mode_info()['mode']
            })

            return f"Limpieza de logs completada: {cleaned_files} archivos eliminados, {total_size / 1024:.2f} KB liberados"

        except Exception as e:
            logger.error(f"Error en limpieza de logs: {e}")
            return f"Error en limpieza: {e}"

# Instancia global de integración de tareas
task_integration = TaskIntegration()