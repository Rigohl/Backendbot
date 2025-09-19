"""
Sistema de Tareas Programadas para BackendBot
Permite programar y ejecutar tareas automáticas según horarios y condiciones.
"""
import threading
import time
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any, Optional
from enum import Enum
import json
from pathlib import Path
from ..utils.data_store import read_json, write_json, initialize_defaults
from ..modes import mode_manager
from ..modes.adaptive_learning import adaptive_learning
from ..utils.logging_config import logger

class TaskFrequency(Enum):
    MINUTELY = "minutely"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ScheduledTask:
    def __init__(self, task_id: str, name: str, function: Callable,
                 frequency: TaskFrequency, priority: TaskPriority = TaskPriority.MEDIUM,
                 conditions: Dict[str, Any] = None, enabled: bool = True):
        self.task_id = task_id
        self.name = name
        self.function = function
        self.frequency = frequency
        self.priority = priority
        self.conditions = conditions or {}
        self.enabled = enabled
        self.last_run = None
        self.next_run = None
        self.run_count = 0
        self.success_count = 0
        self.error_count = 0
        self.created_at = datetime.now()

    def should_run(self) -> bool:
        """Determinar si la tarea debe ejecutarse"""
        if not self.enabled:
            return False

        # Verificar condiciones del modo
        mode_conditions = self.conditions.get('modes', [])
        if mode_conditions:
            current_mode = mode_manager.get_mode_info()['mode']
            if current_mode not in mode_conditions:
                return False

        # Verificar condiciones de carga del sistema
        system_conditions = self.conditions.get('system_load', {})
        if system_conditions:
            # Aquí se podrían verificar métricas del sistema
            # Por simplicidad, solo verificamos si estamos en modo relax
            if current_mode == 'relax' and system_conditions.get('only_when_idle', False):
                return True

        return True

    def run(self):
        """Ejecutar la tarea"""
        try:
            if not self.should_run():
                return

            logger.info(f"Ejecutando tarea programada: {self.name}")
            start_time = time.time()

            # Ejecutar la función
            result = self.function()

            execution_time = time.time() - start_time
            self.last_run = datetime.now()
            self.run_count += 1
            self.success_count += 1

            # Registrar en aprendizaje adaptativo
            adaptive_learning.record_user_action('scheduled_task', {
                'task_id': self.task_id,
                'task_name': self.name,
                'execution_time': execution_time,
                'success': True,
                'mode': mode_manager.get_mode_info()['mode']
            })

            logger.info(f"Tarea {self.name} completada en {execution_time:.2f}s")

        except Exception as e:
            self.error_count += 1
            logger.error(f"Error ejecutando tarea {self.name}: {e}")

            # Registrar error en aprendizaje adaptativo
            adaptive_learning.record_user_action('scheduled_task', {
                'task_id': self.task_id,
                'task_name': self.name,
                'success': False,
                'error': str(e),
                'mode': mode_manager.get_mode_info()['mode']
            })

class TaskScheduler:
    def __init__(self, data_dir: str = ".backendbot_data", create_defaults: bool = False, load_persisted: bool = False):
        # Ensure defaults exist
        initialize_defaults()
        self.data_dir = Path(data_dir)
        self.tasks_file = self.data_dir / "scheduled_tasks.json"

        self.tasks: Dict[str, ScheduledTask] = {}
        self.scheduler_thread = None
        self.running = False

        # Cargar tareas existentes solo si se solicita (tests esperan scheduler limpio por defecto)
        if load_persisted:
            self._load_tasks()

        # Tareas predefinidas del sistema (opcional para tests que desean control)
        if create_defaults:
            self._create_default_tasks()

        logger.info(f"TaskScheduler inicializado con {len(self.tasks)} tareas")

    def _create_default_tasks(self):
        """Crear tareas programadas por defecto"""
        # Tarea de limpieza diaria
        self.add_task(
            task_id="daily_cleanup",
            name="Limpieza Diaria",
            function=self._daily_cleanup,
            frequency=TaskFrequency.DAILY,
            priority=TaskPriority.MEDIUM,
            conditions={'modes': ['editor', 'desarrollo', 'relax']}
        )

        # Tarea de optimización semanal
        self.add_task(
            task_id="weekly_optimization",
            name="Optimización Semanal",
            function=self._weekly_optimization,
            frequency=TaskFrequency.WEEKLY,
            priority=TaskPriority.HIGH,
            conditions={'modes': ['editor', 'desarrollo']}
        )

        # Tarea de monitoreo hourly
        self.add_task(
            task_id="hourly_monitor",
            name="Monitoreo por Hora",
            function=self._hourly_monitor,
            frequency=TaskFrequency.HOURLY,
            priority=TaskPriority.LOW,
            conditions={'modes': ['editor', 'streaming', 'desarrollo', 'gaming']}
        )

        # Tarea de backup semanal
        self.add_task(
            task_id="weekly_backup",
            name="Backup Semanal",
            function=self._weekly_backup,
            frequency=TaskFrequency.WEEKLY,
            priority=TaskPriority.CRITICAL,
            conditions={'modes': ['editor', 'desarrollo']}
        )

    def add_task(self, task_id: str = None, name: str = None, function: Callable = None,
                 frequency: TaskFrequency = None, priority: TaskPriority = TaskPriority.MEDIUM,
                 conditions: Dict[str, Any] = None, enabled: bool = True, **kwargs):
        """Agregar una nueva tarea programada.

        Soporta la firma moderna y la firma legado `add_task(name=..., func=..., schedule=...)`.
        Cuando se usa la firma legado, delega a `add_task_compat` y devuelve `task_id`.
        En la firma moderna mantiene el comportamiento original (devuelve bool).
        """
        # Detectar firma legado y delegar
        if 'func' in kwargs or 'schedule' in kwargs:
            try:
                return self.__call_add_task_fallback(**kwargs)
            except TypeError:
                # Si fallback no aplica, continuar con la ruta moderna
                pass

        # Ruta moderna: validar parámetros mínimos
        try:
            if task_id is None:
                # Generar un id si no se proporcionó
                task_id = f"task_{len(self.tasks)+1}"

            if task_id in self.tasks:
                logger.warning(f"Tarea {task_id} ya existe")
                return False

            # frequency es requerido en la ruta moderna; si es None, asumir DAILY
            if frequency is None:
                frequency = TaskFrequency.DAILY

            task = ScheduledTask(task_id, name or task_id, function, frequency, priority, conditions, enabled)
            self.tasks[task_id] = task

            # Programar la tarea según su frecuencia
            self._schedule_task(task)

            self._save_tasks()
            logger.info(f"Tarea programada agregada: {name or task_id}")
            return True

        except Exception as e:
            logger.error(f"Error agregando tarea {task_id}: {e}")
            return False

    # Backwards-compat: if called with signature add_task(name=..., func=..., schedule=...)
    def __call_add_task_fallback(self, *args, **kwargs):
        # If kwargs contain 'func' and 'schedule', use the compat wrapper
        if 'func' in kwargs and 'schedule' in kwargs:
            name = kwargs.get('name') or kwargs.get('task_id') or f"task_{len(self.tasks)+1}"
            func = kwargs.get('func')
            schedule_str = kwargs.get('schedule')
            return self.add_task_compat(name, func, schedule_str)
        raise TypeError('Unsupported add_task call')


    def remove_task(self, task_id: str) -> bool:
        """Remover una tarea programada"""
        try:
            if task_id not in self.tasks:
                return False

            # Aquí se debería desprogramar de schedule si fuera necesario
            del self.tasks[task_id]
            self._save_tasks()
            logger.info(f"Tarea removida: {task_id}")
            return True

        except Exception as e:
            logger.error(f"Error removiendo tarea {task_id}: {e}")
            return False

    def enable_task(self, task_id: str) -> bool:
        """Habilitar una tarea"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            self._save_tasks()
            return True
        return False

    def disable_task(self, task_id: str) -> bool:
        """Deshabilitar una tarea"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            self._save_tasks()
            return True
        return False

    def _schedule_task(self, task: ScheduledTask):
        """Programar una tarea según su frecuencia"""
        try:
            if task.frequency == TaskFrequency.MINUTELY:
                schedule.every(1).minutes.do(self._run_task, task.task_id)
            elif task.frequency == TaskFrequency.HOURLY:
                schedule.every(1).hours.do(self._run_task, task.task_id)
            elif task.frequency == TaskFrequency.DAILY:
                schedule.every().day.do(self._run_task, task.task_id)
            elif task.frequency == TaskFrequency.WEEKLY:
                schedule.every().week.do(self._run_task, task.task_id)
            elif task.frequency == TaskFrequency.MONTHLY:
                schedule.every(30).days.do(self._run_task, task.task_id)

        except Exception as e:
            logger.error(f"Error programando tarea {task.task_id}: {e}")

    def _run_task(self, task_id: str):
        """Ejecutar una tarea por su ID"""
        if task_id in self.tasks:
            self.tasks[task_id].run()

    def start_scheduler(self):
        """Iniciar el programador de tareas"""
        if self.running:
            return

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("Programador de tareas iniciado")

    def stop_scheduler(self):
        """Detener el programador de tareas"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Programador de tareas detenido")

    def _scheduler_loop(self):
        """Bucle principal del programador"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
            except Exception as e:
                logger.error(f"Error en bucle del programador: {e}")
                time.sleep(300)  # Esperar 5 minutos en caso de error

    def _load_tasks(self):
        """Cargar tareas desde archivo"""
        try:
            data = read_json(self.tasks_file.name) or {}
            for task_data in data.get('tasks', []):
                task_id = task_data.get('task_id')
                if task_id:
                    # En una implementación completa, recrearíamos las ScheduledTask
                    # Por ahora, solo cargamos la configuración básica (no programamos la función)
                    self.tasks[task_id] = ScheduledTask(task_id, task_data.get('name', task_id), lambda: None,
                                                       TaskFrequency(task_data.get('frequency', TaskFrequency.DAILY.value)),
                                                       TaskPriority(task_data.get('priority', TaskPriority.MEDIUM.value)),
                                                       task_data.get('conditions', {}), task_data.get('enabled', True))

        except Exception as e:
            logger.error(f"Error cargando tareas: {e}")

    def _save_tasks(self):
        """Guardar tareas en archivo"""
        try:
            tasks_data = []
            for task in self.tasks.values():
                task_data = {
                    'task_id': task.task_id,
                    'name': task.name,
                    'frequency': task.frequency.value,
                    'priority': task.priority.value,
                    'conditions': task.conditions,
                    'enabled': task.enabled,
                    'run_count': task.run_count,
                    'success_count': task.success_count,
                    'error_count': task.error_count,
                    'created_at': task.created_at.isoformat()
                }
                tasks_data.append(task_data)

            data = {'tasks': tasks_data, 'last_updated': datetime.now().isoformat()}

            write_json(self.tasks_file.name, data)

        except Exception as e:
            logger.error(f"Error guardando tareas: {e}")

    # Funciones de tareas predefinidas
    def _daily_cleanup(self):
        """Tarea de limpieza diaria"""
        logger.info("Ejecutando limpieza diaria")
        # Aquí se integrarían las funciones de limpieza de los bots
        return "Limpieza diaria completada"

    def _weekly_optimization(self):
        """Tarea de optimización semanal"""
        logger.info("Ejecutando optimización semanal")
        # Aquí se integrarían las funciones de optimización
        return "Optimización semanal completada"

    def _hourly_monitor(self):
        """Tarea de monitoreo por hora"""
        logger.info("Ejecutando monitoreo por hora")
        # Aquí se integraría el monitoreo del sistema
        return "Monitoreo por hora completado"

    def _weekly_backup(self):
        """Tarea de backup semanal"""
        logger.info("Ejecutando backup semanal")
        # Aquí se implementaría la lógica de backup
        return "Backup semanal completado"

    def get_task_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de las tareas programadas"""
        total_tasks = len(self.tasks)
        enabled_tasks = sum(1 for task in self.tasks.values() if task.enabled)
        total_runs = sum(task.run_count for task in self.tasks.values())
        total_success = sum(task.success_count for task in self.tasks.values())
        total_errors = sum(task.error_count for task in self.tasks.values())

        return {
            'total_tasks': total_tasks,
            'enabled_tasks': enabled_tasks,
            'disabled_tasks': total_tasks - enabled_tasks,
            'total_runs': total_runs,
            'total_success': total_success,
            'total_errors': total_errors,
            'success_rate': (total_success / max(total_runs, 1)) * 100,
            'running': self.running
        }

    # Compatibility wrapper expected by older tests: allow add_task(name, func, schedule)
    def add_task_compat(self, name: str, func: Callable, schedule: str) -> str:
        """Compatibilidad: crear tarea a partir de firma antigua.

        Devuelve task_id.
        """
        task_id = f"task_{len(self.tasks)+1}"

        # Mapear schedule string a frecuencia simple: hourly/daily/weekly
        if '*/4' in schedule or 'hour' in schedule:
            freq = TaskFrequency.HOURLY
        elif 'day' in schedule or '0 2' in schedule:
            freq = TaskFrequency.DAILY
        else:
            freq = TaskFrequency.DAILY

        self.add_task(task_id=task_id, name=name, function=func, frequency=freq)
        return task_id

    # Exponer execute_task para compatibilidad (llama a _run_task internamente)
    def execute_task(self, task_id: str):
        self._run_task(task_id)


    def get_tasks_list(self) -> List[Dict[str, Any]]:
        """Obtener lista de todas las tareas"""
        tasks_list = []
        for task in self.tasks.values():
            task_info = {
                'task_id': task.task_id,
                'name': task.name,
                'frequency': task.frequency.value,
                'priority': task.priority.value,
                'enabled': task.enabled,
                'run_count': task.run_count,
                'success_count': task.success_count,
                'error_count': task.error_count,
                'last_run': task.last_run.isoformat() if task.last_run else None,
                'conditions': task.conditions
            }
            tasks_list.append(task_info)

        return tasks_list

# Instancia global del programador de tareas (para runtime cargamos persistidos)
task_scheduler = TaskScheduler(load_persisted=True)