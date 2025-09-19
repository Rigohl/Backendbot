"""
BackendBot API - UI/Dashboard Router
Datos y endpoints para la interfaz gráfica y dashboard
"""
import psutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backendbot.packages.models.models import (
    SystemMetrics, BotStatus, NotificationInfo, NotificationType,
    PowerInfo, BackupInfo, BackupType
)
from backendbot.core.di.container import container

router = APIRouter(prefix="/api/v1/ui", tags=["ui", "dashboard"])

# Modelos de respuesta
class DashboardDataResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]
    timestamp: datetime

class BotStatusWidget(BaseModel):
    bot_name: str
    status: BotStatus
    uptime: Optional[timedelta]
    last_activity: datetime
    metrics: SystemMetrics

class NotificationWidget(BaseModel):
    id: str
    title: str
    message: str
    type: str
    timestamp: datetime
    read: bool

class PowerWidget(BaseModel):
    battery_percent: Optional[float]
    power_plugged: bool
    charging: bool
    time_remaining: Optional[timedelta]
    current_profile: str

class BackupWidget(BaseModel):
    last_backup: Optional[datetime]
    next_backup: Optional[datetime]
    status: str
    total_backups: int

@router.get("/dashboard", response_model=DashboardDataResponse)
async def get_dashboard_data():
    """
    Obtener datos completos para el dashboard principal.
    """
    try:
        # Obtener datos de sistema
        system_metrics = await get_system_metrics_data()

        # Obtener datos de bots
        bots_data = await get_bots_status_data()

        # Obtener datos de notificaciones recientes
        notifications_data = await get_recent_notifications()

        # Obtener datos de energía
        power_data = await get_power_data()

        # Obtener datos de backup
        backup_data = await get_backup_data()

        dashboard_data = {
            "system_metrics": system_metrics,
            "bots_status": bots_data,
            "recent_notifications": notifications_data,
            "power_info": power_data,
            "backup_info": backup_data,
            "timestamp": datetime.now()
        }

        return DashboardDataResponse(
            success=True,
            message="Dashboard data retrieved successfully",
            data=dashboard_data,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard data: {str(e)}")

@router.get("/system-metrics")
async def get_system_metrics_data():
    """
    Obtener métricas del sistema para widgets.
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()

        return {
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "memory_used": memory.used,
            "memory_total": memory.total,
            "disk_usage": disk.percent,
            "disk_used": disk.used,
            "disk_total": disk.total,
            "network_sent": network.bytes_sent,
            "network_recv": network.bytes_recv,
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "memory_used": 0,
            "memory_total": 0,
            "disk_usage": 0.0,
            "disk_used": 0,
            "disk_total": 0,
            "network_sent": 0,
            "network_recv": 0,
            "timestamp": datetime.now(),
            "error": str(e)
        }

@router.get("/bots-status")
async def get_bots_status_data():
    """
    Obtener estado de todos los bots para widgets.
    """
    try:
        from backendbot.packages.bots.monitor_worker import MonitorWorker
        from backendbot.packages.bots.organizer_worker import OrganizerWorker
        from backendbot.packages.bots.indexer_worker import IndexerWorker
        from backendbot.packages.bots.guardian_worker import GuardianWorker

        bots = {
            "monitor": MonitorWorker(),
            "organizer": OrganizerWorker(),
            "indexer": IndexerWorker(),
            "guardian": GuardianWorker()
        }

        bots_status = []
        for bot_name, bot_instance in bots.items():
            status = BotStatus.RUNNING if bot_instance.is_alive() else BotStatus.STOPPED
            metrics = bot_instance.get_metrics() if hasattr(bot_instance, 'get_metrics') else SystemMetrics()

            bots_status.append({
                "bot_name": bot_name,
                "status": status.value,
                "uptime": None,  # TODO: Implementar cálculo de uptime
                "last_activity": datetime.now(),
                "metrics": metrics.dict() if hasattr(metrics, 'dict') else {}
            })

        return bots_status
    except Exception as e:
        return [{"error": str(e)}]

@router.get("/recent-notifications")
async def get_recent_notifications(limit: int = 10):
    """
    Obtener notificaciones recientes para widgets.
    """
    try:
        # TODO: Integrar con el sistema de notificaciones real
        # Por ahora, devolver datos de ejemplo
        return [
            {
                "id": "1",
                "title": "Sistema Iniciado",
                "message": "BackendBot se ha iniciado correctamente",
                "type": "info",
                "timestamp": datetime.now(),
                "read": False
            },
            {
                "id": "2",
                "title": "Monitor Activo",
                "message": "El bot Monitor está funcionando correctamente",
                "type": "success",
                "timestamp": datetime.now(),
                "read": False
            }
        ]
    except Exception as e:
        return []

@router.get("/power-info")
async def get_power_data():
    """
    Obtener información de energía para widgets.
    """
    try:
        battery = psutil.sensors_battery()
        if battery:
            return {
                "battery_percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "charging": battery.charging if hasattr(battery, 'charging') else False,
                "time_remaining": timedelta(seconds=battery.secsleft) if battery.secsleft != -1 else None,
                "current_profile": "balanced"  # TODO: Integrar con power manager
            }
        else:
            return {
                "battery_percent": None,
                "power_plugged": True,
                "charging": False,
                "time_remaining": None,
                "current_profile": "balanced"
            }
    except Exception as e:
        return {
            "battery_percent": None,
            "power_plugged": True,
            "charging": False,
            "time_remaining": None,
            "current_profile": "balanced",
            "error": str(e)
        }

@router.get("/backup-info")
async def get_backup_data():
    """
    Obtener información de backups para widgets.
    """
    try:
        # TODO: Integrar con el sistema de backups real
        return {
            "last_backup": datetime.now() - timedelta(hours=2),
            "next_backup": datetime.now() + timedelta(hours=22),
            "status": "success",
            "total_backups": 15
        }
    except Exception as e:
        return {
            "last_backup": None,
            "next_backup": None,
            "status": "unknown",
            "total_backups": 0,
            "error": str(e)
        }

@router.get("/charts/cpu-history")
async def get_cpu_history(hours: int = 1):
    """
    Obtener historial de uso de CPU para gráficos.
    """
    try:
        # TODO: Implementar historial real desde base de datos
        # Por ahora, devolver datos de ejemplo
        data_points = []
        base_time = datetime.now() - timedelta(hours=hours)

        for i in range(60):  # 60 puntos de datos
            data_points.append({
                "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
                "cpu_usage": psutil.cpu_percent() + (i % 10 - 5)  # Variación aleatoria
            })

        return {
            "success": True,
            "message": "CPU history retrieved successfully",
            "data": data_points,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving CPU history: {str(e)}")

@router.get("/charts/memory-history")
async def get_memory_history(hours: int = 1):
    """
    Obtener historial de uso de memoria para gráficos.
    """
    try:
        # TODO: Implementar historial real desde base de datos
        data_points = []
        base_time = datetime.now() - timedelta(hours=hours)

        for i in range(60):
            memory = psutil.virtual_memory()
            data_points.append({
                "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
                "memory_usage": memory.percent + (i % 5 - 2)
            })

        return {
            "success": True,
            "message": "Memory history retrieved successfully",
            "data": data_points,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving memory history: {str(e)}")