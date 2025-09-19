#!/usr/bin/env python3
"""
Sistema de Backup Inteligente - BackendBot
Implementa estrategias de backup incremental, diferencial y completo
"""
import os
import sys
import json
import shutil
import hashlib
import sqlite3
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import gzip
import zipfile

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from backendbot.core.di.container import container

class BackupType(Enum):
    """Tipos de backup disponibles"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"

@dataclass
class BackupJob:
    """Configuración de un trabajo de backup"""
    name: str
    source_paths: List[str]
    destination_path: str
    backup_type: BackupType
    schedule: str  # "daily", "weekly", "monthly"
    retention_days: int
    compression: bool = True
    encryption: bool = False
    exclude_patterns: List[str] = None
    enabled: bool = True

@dataclass
class BackupResult:
    """Resultado de una operación de backup"""
    job_name: str
    backup_type: BackupType
    timestamp: datetime
    success: bool
    total_files: int
    total_size: int
    compressed_size: int
    duration: timedelta
    error_message: Optional[str] = None

class BackupManager:
    """Gestor inteligente de backups"""

    def __init__(self):
        self.logger = container.get_logger()
        self.config = container.get_config_manager()

        # Base de datos para tracking de backups
        self.db_path = os.path.join(os.path.dirname(__file__), 'data', 'backup_tracking.db')
        self._init_database()

        # Jobs de backup
        self.jobs: Dict[str, BackupJob] = {}
        self.backup_history: List[BackupResult] = []

        self._load_jobs()

    def _init_database(self):
        """Inicializa la base de datos de tracking"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS file_hashes (
                    path TEXT PRIMARY KEY,
                    hash TEXT,
                    size INTEGER,
                    mtime REAL,
                    last_backup TEXT
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS backup_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_name TEXT,
                    backup_type TEXT,
                    timestamp TEXT,
                    success BOOLEAN,
                    total_files INTEGER,
                    total_size INTEGER,
                    compressed_size INTEGER,
                    duration REAL,
                    error_message TEXT
                )
            ''')

    def _load_jobs(self):
        """Carga los trabajos de backup desde configuración"""
        default_jobs = [
            BackupJob(
                name="system_config",
                source_paths=[
                    os.path.join(os.path.dirname(__file__), 'config'),
                    os.path.join(os.path.dirname(__file__), 'data')
                ],
                destination_path=os.path.join(os.path.dirname(__file__), 'backups', 'config'),
                backup_type=BackupType.INCREMENTAL,
                schedule="daily",
                retention_days=30,
                compression=True,
                exclude_patterns=["*.tmp", "*.log"]
            ),
            BackupJob(
                name="user_documents",
                source_paths=[
                    os.path.expanduser("~/Documents"),
                    os.path.expanduser("~/Desktop")
                ],
                destination_path=os.path.join(os.path.dirname(__file__), 'backups', 'documents'),
                backup_type=BackupType.DIFFERENTIAL,
                schedule="weekly",
                retention_days=90,
                compression=True
            )
        ]

        # Cargar jobs desde configuración o usar defaults
        configured_jobs = self.config.get('backup.jobs', [])
        if configured_jobs:
            for job_data in configured_jobs:
                job = BackupJob(**job_data)
                self.jobs[job.name] = job
        else:
            for job in default_jobs:
                self.jobs[job.name] = job

    def create_backup_job(self, job: BackupJob):
        """Crea un nuevo trabajo de backup"""
        self.jobs[job.name] = job
        self._save_jobs()
        self.logger.info(f"Trabajo de backup '{job.name}' creado")

    def run_backup(self, job_name: str) -> BackupResult:
        """Ejecuta un backup para un trabajo específico"""
        if job_name not in self.jobs:
            error_msg = f"Trabajo '{job_name}' no encontrado"
            self.logger.error(error_msg)
            return BackupResult(
                job_name=job_name,
                backup_type=BackupType.FULL,
                timestamp=datetime.now(),
                success=False,
                total_files=0,
                total_size=0,
                compressed_size=0,
                duration=timedelta(0),
                error_message=error_msg
            )

        job = self.jobs[job_name]
        start_time = datetime.now()

        try:
            self.logger.info(f"Iniciando backup '{job_name}' ({job.backup_type.value})")

            # Crear directorio de destino
            os.makedirs(job.destination_path, exist_ok=True)

            # Determinar archivos a respaldar
            files_to_backup = self._get_files_to_backup(job)

            if not files_to_backup:
                self.logger.warning(f"No hay archivos para respaldar en '{job_name}'")
                return BackupResult(
                    job_name=job_name,
                    backup_type=job.backup_type,
                    timestamp=start_time,
                    success=True,
                    total_files=0,
                    total_size=0,
                    compressed_size=0,
                    duration=datetime.now() - start_time
                )

            # Crear archivo de backup
            backup_filename = self._create_backup_filename(job, start_time)
            backup_path = os.path.join(job.destination_path, backup_filename)

            # Ejecutar backup según tipo
            if job.backup_type == BackupType.FULL:
                result = self._run_full_backup(job, files_to_backup, backup_path)
            elif job.backup_type == BackupType.INCREMENTAL:
                result = self._run_incremental_backup(job, files_to_backup, backup_path)
            elif job.backup_type == BackupType.DIFFERENTIAL:
                result = self._run_differential_backup(job, files_to_backup, backup_path)

            # Actualizar base de datos
            self._update_file_tracking(job, files_to_backup)

            # Limpiar backups antiguos
            self._cleanup_old_backups(job)

            duration = datetime.now() - start_time
            result.duration = duration

            self.backup_history.append(result)
            self.logger.info(f"Backup '{job_name}' completado en {duration}")

            return result

        except Exception as e:
            error_msg = f"Error en backup '{job_name}': {str(e)}"
            self.logger.error(error_msg)

            return BackupResult(
                job_name=job_name,
                backup_type=job.backup_type,
                timestamp=start_time,
                success=False,
                total_files=0,
                total_size=0,
                compressed_size=0,
                duration=datetime.now() - start_time,
                error_message=error_msg
            )

    def _get_files_to_backup(self, job: BackupJob) -> List[str]:
        """Obtiene la lista de archivos a respaldar"""
        files_to_backup = []

        for source_path in job.source_paths:
            if not os.path.exists(source_path):
                self.logger.warning(f"Ruta fuente no existe: {source_path}")
                continue

            for root, dirs, files in os.walk(source_path):
                # Excluir directorios según patrones
                dirs[:] = [d for d in dirs if not self._should_exclude(os.path.join(root, d), job.exclude_patterns)]

                for file in files:
                    file_path = os.path.join(root, file)

                    # Excluir archivos según patrones
                    if self._should_exclude(file_path, job.exclude_patterns):
                        continue

                    files_to_backup.append(file_path)

        return files_to_backup

    def _should_exclude(self, path: str, exclude_patterns: List[str]) -> bool:
        """Verifica si un archivo/directorio debe ser excluido"""
        if not exclude_patterns:
            return False

        path_str = str(path)
        for pattern in exclude_patterns:
            if pattern in path_str:
                return True
        return False

    def _create_backup_filename(self, job: BackupJob, timestamp: datetime) -> str:
        """Crea el nombre del archivo de backup"""
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        extension = ".zip" if job.compression else ".tar"
        return f"{job.name}_{job.backup_type.value}_{timestamp_str}{extension}"

    def _run_full_backup(self, job: BackupJob, files: List[str], backup_path: str) -> BackupResult:
        """Ejecuta un backup completo"""
        total_size = 0
        total_files = len(files)

        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files:
                if os.path.exists(file_path):
                    zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(job.source_paths[0])))
                    total_size += os.path.getsize(file_path)

        compressed_size = os.path.getsize(backup_path)

        return BackupResult(
            job_name=job.name,
            backup_type=BackupType.FULL,
            timestamp=datetime.now(),
            success=True,
            total_files=total_files,
            total_size=total_size,
            compressed_size=compressed_size,
            duration=timedelta(0)
        )

    def _run_incremental_backup(self, job: BackupJob, files: List[str], backup_path: str) -> BackupResult:
        """Ejecuta un backup incremental"""
        changed_files = []
        total_size = 0
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False) as conn:
            for file_path in files:
                if os.path.exists(file_path):
                    current_hash = self._calculate_file_hash(file_path)
                    stored_data = conn.execute(
                        "SELECT hash, mtime FROM file_hashes WHERE path = ?",
                        (file_path,)
                    ).fetchone()

                    if (not stored_data or
                        stored_data[0] != current_hash or
                        stored_data[1] != os.path.getmtime(file_path)):

                        changed_files.append(file_path)
                        total_size += os.path.getsize(file_path)

        # Crear backup solo con archivos cambiados
        if changed_files:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in changed_files:
                    zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(job.source_paths[0])))

        compressed_size = os.path.getsize(backup_path) if os.path.exists(backup_path) else 0

        return BackupResult(
            job_name=job.name,
            backup_type=BackupType.INCREMENTAL,
            timestamp=datetime.now(),
            success=True,
            total_files=len(changed_files),
            total_size=total_size,
            compressed_size=compressed_size,
            duration=timedelta(0)
        )

    def _run_differential_backup(self, job: BackupJob, files: List[str], backup_path: str) -> BackupResult:
        """Ejecuta un backup diferencial"""
        # Obtener fecha del último backup completo
        last_full_backup = self._get_last_full_backup_time(job.name)

        changed_files = []
        total_size = 0

        for file_path in files:
            if os.path.exists(file_path):
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if mtime > last_full_backup:
                    changed_files.append(file_path)
                    total_size += os.path.getsize(file_path)

        # Crear backup con archivos cambiados desde último backup completo
        if changed_files:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in changed_files:
                    zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(job.source_paths[0])))

        compressed_size = os.path.getsize(backup_path) if os.path.exists(backup_path) else 0

        return BackupResult(
            job_name=job.name,
            backup_type=BackupType.DIFFERENTIAL,
            timestamp=datetime.now(),
            success=True,
            total_files=len(changed_files),
            total_size=total_size,
            compressed_size=compressed_size,
            duration=timedelta(0)
        )

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcula el hash MD5 de un archivo"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _update_file_tracking(self, job: BackupJob, files: List[str]):
        """Actualiza el tracking de archivos en la base de datos"""
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False) as conn:
            for file_path in files:
                if os.path.exists(file_path):
                    file_hash = self._calculate_file_hash(file_path)
                    mtime = os.path.getmtime(file_path)
                    size = os.path.getsize(file_path)

                    conn.execute('''
                        INSERT OR REPLACE INTO file_hashes
                        (path, hash, size, mtime, last_backup)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (file_path, file_hash, size, mtime, datetime.now().isoformat()))

    def _get_last_full_backup_time(self, job_name: str) -> datetime:
        """Obtiene la fecha del último backup completo"""
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False) as conn:
            result = conn.execute('''
                SELECT timestamp FROM backup_history
                WHERE job_name = ? AND backup_type = ? AND success = 1
                ORDER BY timestamp DESC LIMIT 1
            ''', (job_name, BackupType.FULL.value)).fetchone()

        if result:
            return datetime.fromisoformat(result[0])
        return datetime.min

    def _cleanup_old_backups(self, job: BackupJob):
        """Limpia backups antiguos según política de retención"""
        try:
            cutoff_date = datetime.now() - timedelta(days=job.retention_days)

            for filename in os.listdir(job.destination_path):
                if filename.startswith(job.name):
                    file_path = os.path.join(job.destination_path, filename)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

                    if file_mtime < cutoff_date:
                        os.remove(file_path)
                        self.logger.info(f"Backup antiguo eliminado: {filename}")

        except Exception as e:
            self.logger.error(f"Error limpiando backups antiguos: {e}")

    def _save_jobs(self):
        """Guarda los trabajos de backup en configuración"""
        jobs_data = [vars(job) for job in self.jobs.values()]
        self.config.set('backup.jobs', jobs_data)

    def get_backup_history(self, job_name: Optional[str] = None, limit: int = 50) -> List[BackupResult]:
        """Obtiene historial de backups"""
        with sqlite3.connect(self.db_path) as conn:
            if job_name:
                results = conn.execute('''
                    SELECT * FROM backup_history
                    WHERE job_name = ?
                    ORDER BY timestamp DESC LIMIT ?
                ''', (job_name, limit)).fetchall()
            else:
                results = conn.execute('''
                    SELECT * FROM backup_history
                    ORDER BY timestamp DESC LIMIT ?
                ''', (limit,)).fetchall()

        history = []
        for row in results:
            history.append(BackupResult(
                job_name=row[1],
                backup_type=BackupType(row[2]),
                timestamp=datetime.fromisoformat(row[3]),
                success=bool(row[4]),
                total_files=row[5],
                total_size=row[6],
                compressed_size=row[7],
                duration=timedelta(seconds=row[8]),
                error_message=row[9]
            ))

        return history

    def restore_backup(self, backup_path: str, restore_path: str) -> bool:
        """Restaura un backup"""
        try:
            self.logger.info(f"Restaurando backup: {backup_path}")

            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(restore_path)

            self.logger.info(f"Backup restaurado exitosamente en: {restore_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error restaurando backup: {e}")
            return False

    def get_backup_stats(self) -> Dict:
        """Obtiene estadísticas de backups"""
        with sqlite3.connect(self.db_path) as conn:
            total_backups = conn.execute("SELECT COUNT(*) FROM backup_history").fetchone()[0]
            successful_backups = conn.execute("SELECT COUNT(*) FROM backup_history WHERE success = 1").fetchone()[0]
            total_size = conn.execute("SELECT SUM(total_size) FROM backup_history WHERE success = 1").fetchone()[0] or 0
            compressed_size = conn.execute("SELECT SUM(compressed_size) FROM backup_history WHERE success = 1").fetchone()[0] or 0

        return {
            'total_backups': total_backups,
            'successful_backups': successful_backups,
            'success_rate': (successful_backups / total_backups * 100) if total_backups > 0 else 0,
            'total_size_gb': total_size / (1024**3),
            'compressed_size_gb': compressed_size / (1024**3),
            'compression_ratio': (1 - compressed_size / total_size) * 100 if total_size > 0 else 0
        }

# Instancia global
backup_manager = BackupManager()

if __name__ == "__main__":
    # Demo del sistema de backup inteligente
    print("💾 Demo del Sistema de Backup Inteligente")

    # Mostrar trabajos disponibles
    print(f"📋 Trabajos de backup configurados: {list(backup_manager.jobs.keys())}")

    # Ejecutar backup de configuración
    print("\n🔄 Ejecutando backup de configuración...")
    result = backup_manager.run_backup("system_config")

    print(f"✅ Backup completado: {result.success}")
    print(f"📁 Archivos respaldados: {result.total_files}")
    print(f"💾 Tamaño original: {result.total_size / 1024:.1f} KB")
    print(f"📦 Tamaño comprimido: {result.compressed_size / 1024:.1f} KB")
    print(f"⏱️ Duración: {result.duration}")

    # Mostrar estadísticas
    stats = backup_manager.get_backup_stats()
    print(f"\n📊 Estadísticas: {json.dumps(stats, indent=2, default=str)}")

    print("\n✅ Sistema de backup inteligente inicializado correctamente!")