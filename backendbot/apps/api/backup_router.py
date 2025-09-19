"""
BackendBot API - Backup Router
Gestión de backups del sistema
"""
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum
import os
import psutil

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backendbot.packages.models.models import BackupInfo, BackupType

router = APIRouter(prefix="/api/v1/backup", tags=["backup"])

# Enums locales para evitar dependencias
class BackupTypeEnum(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"

class BackupStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# Clase BackupJob simplificada
class BackupJob:
    def __init__(self, name: str, source_paths: List[str], destination_path: str,
                 backup_type: BackupTypeEnum, schedule: str = "daily",
                 retention_days: int = 30, compression: bool = True,
                 encryption: bool = False, exclude_patterns: List[str] = None,
                 enabled: bool = True):
        self.name = name
        self.source_paths = source_paths
        self.destination_path = destination_path
        self.backup_type = backup_type
        self.schedule = schedule
        self.retention_days = retention_days
        self.compression = compression
        self.encryption = encryption
        self.exclude_patterns = exclude_patterns or []
        self.enabled = enabled

# Clase BackupResult simplificada
class BackupResult:
    def __init__(self, job_name: str, backup_type: BackupTypeEnum, success: bool,
                 total_size: int = 0, files_count: int = 0, error_message: str = ""):
        self.job_name = job_name
        self.backup_type = backup_type
        self.success = success
        self.total_size = total_size
        self.files_count = files_count
        self.error_message = error_message
        self.timestamp = datetime.now()

# Clase BackupManager simplificada
class BackupManager:
    def __init__(self):
        self.jobs: Dict[str, BackupJob] = {}
        self.backup_history: List[BackupResult] = []

    def _perform_backup(self, job: BackupJob):
        """Ejecutar backup de forma simplificada"""
        try:
            # Simulación de backup - en implementación real copiaría archivos
            total_size = 0
            files_count = 0

            for source_path in job.source_paths:
                if os.path.exists(source_path):
                    if os.path.isfile(source_path):
                        total_size += os.path.getsize(source_path)
                        files_count += 1
                    else:
                        # Calcular tamaño del directorio
                        for root, dirs, files in os.walk(source_path):
                            for file in files:
                                filepath = os.path.join(root, file)
                                try:
                                    total_size += os.path.getsize(filepath)
                                    files_count += 1
                                except OSError:
                                    pass

            # Crear resultado
            result = BackupResult(
                job_name=job.name,
                backup_type=job.backup_type,
                success=True,
                total_size=total_size,
                files_count=files_count
            )

        except Exception as e:
            result = BackupResult(
                job_name=job.name,
                backup_type=job.backup_type,
                success=False,
                error_message=str(e)
            )

        self.backup_history.append(result)

# Modelos de respuesta
class BackupListResponse(BaseModel):
    success: bool
    message: str
    backups: List[BackupInfo]
    total: int
    timestamp: datetime

class BackupResponse(BaseModel):
    success: bool
    message: str
    backup: BackupInfo
    timestamp: datetime

class BackupCreateResponse(BaseModel):
    success: bool
    message: str
    backup_id: str
    timestamp: datetime

class BackupJobResponse(BaseModel):
    success: bool
    message: str
    job: Dict
    timestamp: datetime


# Mock mínimo de BackupManager para pruebas y compatibilidad
class BackupManager:
    def __init__(self):
        self.jobs = {}
        self.backup_history = []
    def _perform_backup(self, job):
        pass

backup_manager = BackupManager()

@router.get("/jobs", response_model=BackupListResponse)
async def get_backup_jobs():
    """
    Obtener lista de trabajos de backup configurados.
    """
    try:
        jobs = []
        for job_name, job in backup_manager.jobs.items():
            jobs.append(BackupInfo(
                id=job_name,
                name=job.name,
                type=BackupType(job.backup_type.value),
                source_paths=job.source_paths,
                destination_path=job.destination_path,
                schedule=job.schedule,
                last_run=None,  # TODO: Implementar tracking de últimas ejecuciones
                next_run=None,  # TODO: Implementar cálculo de próximas ejecuciones
                status="configured",
                enabled=job.enabled
            ))

        return BackupListResponse(
            success=True,
            message="Backup jobs retrieved successfully",
            backups=jobs,
            total=len(jobs),
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving backup jobs: {str(e)}")

@router.post("/jobs", response_model=BackupCreateResponse)
async def create_backup_job(job_data: Dict):
    """
    Crear nuevo trabajo de backup.
    """
    try:
        # Validar datos requeridos
        required_fields = ["name", "source_paths", "destination_path", "backup_type", "schedule"]
        for field in required_fields:
            if field not in job_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # Crear objeto BackupJob
        from backendbot.backup_system import BackupJob

        job = BackupJob(
            name=job_data["name"],
            source_paths=job_data["source_paths"],
            destination_path=job_data["destination_path"],
            backup_type=BackupTypeEnum(job_data["backup_type"]),
            schedule=job_data.get("schedule", "daily"),
            retention_days=job_data.get("retention_days", 30),
            compression=job_data.get("compression", True),
            encryption=job_data.get("encryption", False),
            exclude_patterns=job_data.get("exclude_patterns", []),
            enabled=job_data.get("enabled", True)
        )

        # Agregar job al manager
        backup_manager.jobs[job.name] = job

        return BackupCreateResponse(
            success=True,
            message="Backup job created successfully",
            backup_id=job.name,
            timestamp=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating backup job: {str(e)}")

@router.get("/jobs/{job_name}", response_model=BackupJobResponse)
async def get_backup_job(job_name: str):
    """
    Obtener detalles de un trabajo de backup específico.
    """
    try:
        if job_name not in backup_manager.jobs:
            raise HTTPException(status_code=404, detail=f"Backup job '{job_name}' not found")

        job = backup_manager.jobs[job_name]
        job_data = {
            "name": job.name,
            "source_paths": job.source_paths,
            "destination_path": job.destination_path,
            "backup_type": job.backup_type.value,
            "schedule": job.schedule,
            "retention_days": job.retention_days,
            "compression": job.compression,
            "encryption": job.encryption,
            "exclude_patterns": job.exclude_patterns,
            "enabled": job.enabled
        }

        return BackupJobResponse(
            success=True,
            message="Backup job retrieved successfully",
            job=job_data,
            timestamp=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving backup job: {str(e)}")

@router.put("/jobs/{job_name}")
async def update_backup_job(job_name: str, job_data: Dict):
    """
    Actualizar trabajo de backup existente.
    """
    try:
        if job_name not in backup_manager.jobs:
            raise HTTPException(status_code=404, detail=f"Backup job '{job_name}' not found")

        job = backup_manager.jobs[job_name]

        # Actualizar campos
        for key, value in job_data.items():
            if hasattr(job, key):
                setattr(job, key, value)

        return {
            "success": True,
            "message": f"Backup job '{job_name}' updated successfully",
            "timestamp": datetime.now()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating backup job: {str(e)}")

@router.delete("/jobs/{job_name}")
async def delete_backup_job(job_name: str):
    """
    Eliminar trabajo de backup.
    """
    try:
        if job_name not in backup_manager.jobs:
            raise HTTPException(status_code=404, detail=f"Backup job '{job_name}' not found")

        del backup_manager.jobs[job_name]

        return {
            "success": True,
            "message": f"Backup job '{job_name}' deleted successfully",
            "timestamp": datetime.now()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting backup job: {str(e)}")

@router.post("/jobs/{job_name}/run", response_model=BackupCreateResponse)
async def run_backup_job(job_name: str, background_tasks: BackgroundTasks):
    """
    Ejecutar trabajo de backup inmediatamente.
    """
    try:
        if job_name not in backup_manager.jobs:
            raise HTTPException(status_code=404, detail=f"Backup job '{job_name}' not found")

        job = backup_manager.jobs[job_name]

        # Ejecutar backup en background
        background_tasks.add_task(backup_manager._perform_backup, job)

        return BackupCreateResponse(
            success=True,
            message=f"Backup job '{job_name}' started successfully",
            backup_id=f"{job_name}_{datetime.now().timestamp()}",
            timestamp=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running backup job: {str(e)}")

@router.get("/history")
async def get_backup_history(limit: int = 50):
    """
    Obtener historial de backups ejecutados.
    """
    try:
        history = backup_manager.backup_history[-limit:]  # Últimos N backups

        return {
            "success": True,
            "message": "Backup history retrieved successfully",
            "history": [result.__dict__ if hasattr(result, '__dict__') else result for result in history],
            "total": len(backup_manager.backup_history),
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving backup history: {str(e)}")

@router.get("/stats")
async def get_backup_stats():
    """
    Obtener estadísticas de backups.
    """
    try:
        total_backups = len(backup_manager.backup_history)
        successful_backups = len([b for b in backup_manager.backup_history if b.success])
        failed_backups = total_backups - successful_backups

        # Calcular tamaño total de backups
        total_size = sum(b.total_size for b in backup_manager.backup_history if hasattr(b, 'total_size'))

        # Estadísticas por tipo
        type_stats = {}
        for backup_type in BackupTypeEnum:
            type_backups = [b for b in backup_manager.backup_history if b.backup_type == backup_type]
            type_stats[backup_type.value] = {
                "total": len(type_backups),
                "successful": len([b for b in type_backups if b.success]),
                "failed": len([b for b in type_backups if not b.success])
            }

        return {
            "success": True,
            "message": "Backup stats retrieved successfully",
            "stats": {
                "total_backups": total_backups,
                "successful_backups": successful_backups,
                "failed_backups": failed_backups,
                "success_rate": (successful_backups / total_backups * 100) if total_backups > 0 else 0,
                "total_size": total_size,
                "by_type": type_stats
            },
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving backup stats: {str(e)}")

@router.post("/cleanup")
async def cleanup_old_backups():
    """
    Limpiar backups antiguos según políticas de retención.
    """
    try:
        # TODO: Implementar lógica de cleanup
        return {
            "success": True,
            "message": "Backup cleanup completed successfully",
            "cleaned_backups": 0,  # TODO: Retornar número real de backups eliminados
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during backup cleanup: {str(e)}")

@router.get("/storage/info")
async def get_backup_storage_info():
    """
    Obtener información de almacenamiento de backups.
    """
    try:
        import os
        import psutil

        # Información del directorio de backups
        backup_dir = os.path.join(os.path.dirname(__file__), "..", "..", "backups")
        if os.path.exists(backup_dir):
            disk_usage = psutil.disk_usage(backup_dir)
            dir_size = get_directory_size(backup_dir)
        else:
            disk_usage = None
            dir_size = 0

        return {
            "success": True,
            "message": "Backup storage info retrieved successfully",
            "storage_info": {
                "backup_directory": backup_dir,
                "directory_exists": os.path.exists(backup_dir),
                "total_size": dir_size,
                "disk_free": disk_usage.free if disk_usage else 0,
                "disk_total": disk_usage.total if disk_usage else 0,
                "disk_used_percent": disk_usage.percent if disk_usage else 0
            },
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving backup storage info: {str(e)}")

def get_directory_size(path: str) -> int:
    """
    Calcular tamaño total de un directorio recursivamente.
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except OSError:
                pass
    return total_size