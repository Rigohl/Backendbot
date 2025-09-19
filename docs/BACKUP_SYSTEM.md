# 💾 Sistema de Backup Robusto

## 📋 Descripción General

El Sistema de Backup Robusto de BackendBot proporciona soluciones completas de respaldo con múltiples estrategias, compresión inteligente, verificación de integridad y seguimiento completo de archivos.

## 🚀 Características Principales

- **Múltiples Estrategias**: Incremental, diferencial y completo
- **Compresión Inteligente**: Reducción de tamaño con algoritmos eficientes
- **Verificación de Integridad**: Hashing para detectar corrupciones
- **Base de Datos SQLite**: Seguimiento completo de archivos y versiones
- **Restauración Selectiva**: Recuperar archivos específicos o versiones anteriores
- **Programación Automática**: Backups programados y automáticos
- **Integración Completa**: Funciona con todos los sistemas de BackendBot

## 📁 Estructura del Sistema

```
backup_system/
├── __init__.py
├── backup_manager.py            # Gestor principal de backups
├── backup_strategy.py           # Estrategias de backup
├── compression_engine.py        # Motor de compresión
├── integrity_checker.py         # Verificación de integridad
├── restore_engine.py            # Motor de restauración
├── models/                      # Modelos de datos
│   ├── __init__.py
│   └── backup_models.py         # Modelos Pydantic
└── storage/                     # Base de datos y metadatos
    ├── __init__.py
    ├── backup_database.py       # SQLite para metadatos
    └── file_tracker.py          # Seguimiento de archivos
```

## 🛠️ Uso Básico

### Inicialización
```python
from backup_system import BackupManager

# Crear instancia del gestor
manager = BackupManager()
```

### Backup Completo
```python
# Crear backup completo
result = manager.create_backup(
    job_name="full_backup_2024",
    source_paths=["C:/Users/Documents", "C:/Projects"],
    destination="D:/Backups",
    strategy="full"
)

print(f"Backup completado: {result['files_processed']} archivos")
print(f"Tamaño comprimido: {result['compressed_size_mb']} MB")
```

### Backup Incremental
```python
# Backup incremental (solo cambios desde último backup)
result = manager.create_backup(
    job_name="incremental_backup",
    source_paths=["C:/Users/Documents"],
    destination="D:/Backups",
    strategy="incremental",
    base_backup="full_backup_2024"
)
```

### Backup Diferencial
```python
# Backup diferencial (todos los cambios desde último completo)
result = manager.create_backup(
    job_name="differential_backup",
    source_paths=["C:/Projects"],
    destination="D:/Backups",
    strategy="differential",
    base_backup="full_backup_2024"
)
```

## 🎯 Estrategias de Backup

### Backup Completo
```python
# Configuración completa
full_config = {
    "strategy": "full",
    "compression": "high",  # none, low, medium, high, maximum
    "encryption": True,
    "verify_integrity": True,
    "exclude_patterns": ["*.tmp", "*.log", "node_modules/**"],
    "include_hidden": False
}

result = manager.create_backup(
    job_name="complete_system_backup",
    source_paths=["C:/Users", "C:/Program Files"],
    destination="E:/Backups",
    **full_config
)
```

### Backup Incremental
```python
# Backup incremental inteligente
incremental_config = {
    "strategy": "incremental",
    "base_backup": "full_backup_2024_01_01",
    "track_changes": True,  # Rastrear cambios en tiempo real
    "compression": "medium",
    "max_file_size": 100 * 1024 * 1024  # 100MB máximo por archivo
}

result = manager.create_backup(
    job_name="daily_incremental",
    source_paths=["C:/Users/Documents"],
    destination="D:/Backups",
    **incremental_config
)
```

### Backup Diferencial
```python
# Backup diferencial optimizado
differential_config = {
    "strategy": "differential", 
    "base_backup": "full_backup_2024",
    "compression": "high",
    "parallel_processing": True,  # Procesamiento paralelo
    "buffer_size": 64 * 1024 * 1024  # 64MB buffer
}

result = manager.create_backup(
    job_name="weekly_differential",
    source_paths=["C:/Projects", "C:/Databases"],
    destination="D:/Backups",
    **differential_config
)
```

## 🔄 Restauración de Backups

### Restauración Completa
```python
# Restaurar backup completo
result = manager.restore_backup(
    backup_job="full_backup_2024",
    destination="C:/Restored",
    overwrite_existing=False
)

print(f"Restaurados: {result['files_restored']} archivos")
print(f"Errores: {result['errors_count']}")
```

### Restauración Selectiva
```python
# Restaurar archivos específicos
result = manager.restore_files(
    backup_job="full_backup_2024",
    file_patterns=["*.docx", "*.xlsx"],
    destination="C:/Restored/Documents",
    date_filter="2024-01-*"  # Solo archivos de enero 2024
)
```

### Restauración por Versión
```python
# Restaurar versión específica de archivo
result = manager.restore_file_version(
    file_path="C:/Projects/report.docx",
    version_date="2024-01-15",
    destination="C:/Restored/report_old.docx"
)
```

## 📊 Gestión de Backups

### Listar Backups
```python
# Obtener todos los backups
backups = manager.list_backups()
for backup in backups:
    print(f"Job: {backup['job_name']}")
    print(f"Strategy: {backup['strategy']}")
    print(f"Created: {backup['created_date']}")
    print(f"Size: {backup['total_size_mb']} MB")
    print("---")
```

### Información de Backup
```python
# Detalles de un backup específico
info = manager.get_backup_info("full_backup_2024")
print(f"Archivos: {info['file_count']}")
print(f"Carpetas: {info['folder_count']}")
print(f"Tamaño original: {info['original_size_mb']} MB")
print(f"Tamaño comprimido: {info['compressed_size_mb']} MB")
print(f"Ratio compresión: {info['compression_ratio']}%")
```

### Eliminar Backups
```python
# Eliminar backup específico
manager.delete_backup("old_backup_2023")

# Limpiar backups antiguos (más de 30 días)
manager.cleanup_old_backups(days=30)
```

## ⏰ Programación de Backups

### Backup Diario
```python
# Programar backup diario
schedule_id = manager.schedule_backup(
    job_name="daily_backup",
    source_paths=["C:/Users/Documents"],
    destination="D:/Backups",
    strategy="incremental",
    schedule="daily",
    time="02:00",  # 2 AM
    base_backup="weekly_full_backup"
)
```

### Backup Semanal
```python
# Programar backup semanal completo
schedule_id = manager.schedule_backup(
    job_name="weekly_full_backup",
    source_paths=["C:/Users", "C:/Projects"],
    destination="E:/Backups",
    strategy="full",
    schedule="weekly",
    day_of_week="sunday",
    time="03:00"  # 3 AM domingos
)
```

### Gestión de Programaciones
```python
# Listar programaciones activas
schedules = manager.list_scheduled_backups()

# Cancelar programación
manager.cancel_scheduled_backup(schedule_id)

# Modificar programación
manager.update_schedule(
    schedule_id,
    time="01:00",  # Cambiar hora
    enabled=False  # Deshabilitar temporalmente
)
```

## 🔐 Compresión y Encriptación

### Configuración de Compresión
```python
# Configurar algoritmo de compresión
compression_config = {
    "algorithm": "lzma",  # none, gzip, bz2, lzma, zip
    "level": 9,           # 1-9 para gzip/bz2, 0-9 para lzma
    "buffer_size": 64 * 1024 * 1024,  # 64MB
    "parallel_compression": True
}

manager.set_compression_config(compression_config)
```

### Encriptación de Backups
```python
# Configurar encriptación
encryption_config = {
    "enabled": True,
    "algorithm": "AES256",
    "key_derivation": "PBKDF2",
    "iterations": 100000
}

# Establecer contraseña
manager.set_encryption_password("my_secure_password")

# Aplicar configuración
manager.set_encryption_config(encryption_config)
```

## ✅ Verificación de Integridad

### Verificar Backup
```python
# Verificar integridad de backup
verification = manager.verify_backup("full_backup_2024")
print(f"Archivos verificados: {verification['verified_files']}")
print(f"Archivos corruptos: {verification['corrupted_files']}")
print(f"Estado: {'OK' if verification['is_valid'] else 'ERROR'}")
```

### Reparar Backup
```python
# Intentar reparar archivos corruptos
repair_result = manager.repair_backup("full_backup_2024")
print(f"Archivos reparados: {repair_result['repaired_files']}")
print(f"Archivos irrecuperables: {repair_result['unrecoverable_files']}")
```

## 📈 Monitoreo y Estadísticas

### Estadísticas de Backup
```python
# Obtener estadísticas generales
stats = manager.get_backup_statistics()
print(f"Total backups: {stats['total_backups']}")
print(f"Espacio usado: {stats['total_size_gb']} GB")
print(f"Tasa éxito: {stats['success_rate']}%")
print(f"Tiempo promedio: {stats['avg_backup_time']} min")
```

### Reportes de Rendimiento
```python
# Generar reporte de rendimiento
report = manager.generate_performance_report(days=30)
print("Backup Performance Report:")
print(f"Fastest backup: {report['fastest_backup_time']} min")
print(f"Slowest backup: {report['slowest_backup_time']} min")
print(f"Average compression ratio: {report['avg_compression_ratio']}%")
```

## 🔗 Integración con Otros Sistemas

### Con Notification System
```python
# Notificar sobre backups
manager.on_backup_complete(lambda result:
    notification_manager.send_notification(
        f"Backup completado: {result['job_name']} - {result['files_processed']} archivos",
        "info",
        ["desktop", "email"]
    )
)

manager.on_backup_failed(lambda error:
    notification_manager.send_notification(
        f"Backup fallido: {error['job_name']} - {error['error_message']}",
        "error",
        ["desktop", "email"]
    )
)
```

### Con Power Management
```python
# Optimizar energía durante backups
manager.on_backup_start(lambda:
    power_manager.apply_profile("balanced")  # Estabilidad durante backup
)

manager.on_backup_end(lambda:
    power_manager.apply_profile("power_saver")  # Volver a ahorro
)
```

### Con Dashboard
```python
# Mostrar estado de backups en dashboard
dashboard.add_backup_widget(manager)
```

## 🚨 Manejo de Errores

### Recuperación de Errores
```python
# Configurar política de reintentos
manager.set_retry_policy(
    max_retries=3,
    retry_delay=300,  # 5 minutos
    exponential_backoff=True
)
```

### Logging Avanzado
```python
# Habilitar logging detallado
import logging
logging.getLogger('backup_system').setLevel(logging.DEBUG)

# Configurar archivo de log
manager.set_log_file("C:/Logs/backup_system.log")
```

## 📚 API Reference

### Clase BackupManager

#### Métodos Principales
- `create_backup(job_name, source_paths, destination, strategy, **kwargs)`: Crea backup
- `restore_backup(backup_job, destination, **kwargs)`: Restaura backup
- `list_backups()`: Lista todos los backups
- `get_backup_info(job_name)`: Obtiene información de backup
- `verify_backup(job_name)`: Verifica integridad

#### Métodos de Programación
- `schedule_backup(job_name, source_paths, destination, schedule, **kwargs)`: Programa backup
- `list_scheduled_backups()`: Lista backups programados
- `cancel_scheduled_backup(schedule_id)`: Cancela programación

### Estrategias Disponibles
- `full`: Backup completo de todos los archivos
- `incremental`: Solo archivos modificados desde último backup
- `differential`: Todos los archivos modificados desde último backup completo

## 🔍 Ejemplos Avanzados

### Sistema de Backup Empresarial
```python
from backup_system import BackupManager
import datetime

class EnterpriseBackupSystem:
    def __init__(self):
        self.backup = BackupManager()
        self.setup_backup_policies()
        self.setup_monitoring()
    
    def setup_backup_policies(self):
        """Configura políticas de backup empresariales"""
        
        # Backup completo semanal
        self.backup.schedule_backup(
            job_name="weekly_full_system",
            source_paths=[
                "C:/Users",
                "C:/Program Files/CustomApps", 
                "D:/Databases",
                "E:/SharedDocuments"
            ],
            destination="F:/EnterpriseBackups",
            strategy="full",
            schedule="weekly",
            day_of_week="sunday",
            time="02:00",
            compression="high",
            encryption=True,
            verify_integrity=True,
            retention_days=90  # Mantener 90 días
        )
        
        # Backup incremental diario
        self.backup.schedule_backup(
            job_name="daily_incremental",
            source_paths=["C:/Users/Documents", "D:/Databases"],
            destination="F:/EnterpriseBackups",
            strategy="incremental",
            schedule="daily",
            time="01:00",
            base_backup="weekly_full_system",
            compression="medium",
            retention_days=30
        )
        
        # Backup de configuración cada hora
        self.backup.schedule_backup(
            job_name="hourly_config",
            source_paths=["C:/Config", "C:/Scripts"],
            destination="F:/EnterpriseBackups",
            strategy="full",
            schedule="hourly",
            compression="low",  # Rápido para archivos pequeños
            retention_days=7
        )
    
    def setup_monitoring(self):
        """Configura monitoreo y alertas"""
        
        # Notificar backups exitosos
        self.backup.on_backup_complete(lambda result:
            self.notify_success(result)
        )
        
        # Notificar backups fallidos
        self.backup.on_backup_failed(lambda error:
            self.notify_failure(error)
        )
        
        # Verificar integridad semanalmente
        self.backup.schedule_integrity_check(
            schedule="weekly",
            day_of_week="saturday",
            time="03:00"
        )
    
    def notify_success(self, result):
        """Notificar backup exitoso"""
        message = f"""✅ Backup Completado
Job: {result['job_name']}
Archivos: {result['files_processed']}
Tamaño: {result['compressed_size_mb']} MB
Duración: {result['duration_minutes']} min
Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        # Enviar notificación (integrar con sistema de notificaciones)
        print(message)
    
    def notify_failure(self, error):
        """Notificar backup fallido"""
        message = f"""❌ Backup Fallido
Job: {error['job_name']}
Error: {error['error_message']}
Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        print(message)
        # Aquí se integraría con sistema de alertas
    
    def generate_report(self):
        """Generar reporte semanal"""
        stats = self.backup.get_backup_statistics()
        report = f"""
📊 Reporte Semanal de Backups
==============================
Total backups: {stats['total_backups']}
Espacio usado: {stats['total_size_gb']} GB
Tasa de éxito: {stats['success_rate']}%
Tiempo promedio: {stats['avg_backup_time']} min
Último backup: {stats['last_backup_date']}
"""
        return report
    
    def emergency_restore(self, job_name, priority_files=None):
        """Restauración de emergencia"""
        if priority_files:
            # Restaurar solo archivos críticos primero
            self.backup.restore_files(
                backup_job=job_name,
                file_patterns=priority_files,
                destination="C:/EmergencyRestore",
                priority="high"
            )
        else:
            # Restauración completa
            self.backup.restore_backup(
                backup_job=job_name,
                destination="C:/FullRestore"
            )

# Uso del sistema
backup_system = EnterpriseBackupSystem()

# Generar reporte semanal
print(backup_system.generate_report())

# En caso de emergencia
# backup_system.emergency_restore("weekly_full_system", ["*.db", "*.config"])
```

Este sistema proporciona una solución completa de backup para entornos empresariales con políticas automatizadas, monitoreo continuo y capacidades de recuperación de desastres.</content>
<parameter name="filePath">c:\Users\DELL\Desktop\BackendBot\docs\BACKUP_SYSTEM.md