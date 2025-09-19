# ⚡ Sistema de Gestión Inteligente de Energía

## 📋 Descripción General

El Sistema de Gestión Inteligente de Energía de BackendBot proporciona control automático y manual de los perfiles de energía del sistema, optimizando el consumo basado en la carga de trabajo y condiciones del sistema.

## 🚀 Características Principales

- **Perfiles Adaptativos**: Cambio automático según carga del sistema
- **Monitoreo Térmico**: Control de temperatura y ventiladores
- **Optimización Automática**: Ajustes basados en batería vs. corriente
- **Perfiles Personalizables**: High-performance, balanced, power-saver, ultra-low
- **Monitoreo en Tiempo Real**: Métricas de consumo y eficiencia
- **Integración Completa**: Funciona con todos los sistemas de BackendBot

## 📁 Estructura del Sistema

```
power_management/
├── __init__.py
├── power_manager.py             # Gestor principal de energía
├── power_profile.py             # Definición de perfiles
├── thermal_monitor.py           # Monitoreo térmico
├── battery_monitor.py           # Monitoreo de batería
├── adaptive_controller.py       # Control adaptativo
├── models/                      # Modelos de datos
│   ├── __init__.py
│   └── power_models.py          # Modelos Pydantic
└── storage/                     # Almacenamiento de configuración
    ├── __init__.py
    └── power_storage.py         # SQLite para configuración
```

## 🛠️ Uso Básico

### Inicialización
```python
from power_management import PowerManager

# Crear instancia del gestor
manager = PowerManager()
```

### Aplicar Perfil Manual
```python
# Aplicar perfil de alto rendimiento
manager.apply_profile("high_performance")

# Aplicar perfil equilibrado
manager.apply_profile("balanced")

# Aplicar perfil de ahorro de energía
manager.apply_profile("power_saver")

# Aplicar perfil ultra bajo consumo
manager.apply_profile("ultra_low")
```

### Obtener Estado Actual
```python
# Estado completo del sistema de energía
status = manager.get_power_status()
print(f"Current profile: {status['current_profile']}")
print(f"Battery level: {status['battery_percent']}%")
print(f"Temperature: {status['temperature']}°C")
print(f"Power source: {status['power_source']}")
```

## 🎯 Perfiles de Energía

### Perfil High Performance
```python
# Máximo rendimiento - para tareas intensivas
profile = manager.get_profile("high_performance")
print(f"CPU Max: {profile.cpu_max_freq} MHz")
print(f"GPU Max: {profile.gpu_max_freq} MHz")
print(f"Screen timeout: {profile.screen_timeout} min")
print(f"Sleep timeout: {profile.sleep_timeout} min")
```

### Perfil Balanced
```python
# Equilibrio entre rendimiento y energía
profile = manager.get_profile("balanced")
print(f"CPU Balanced: {profile.cpu_freq_range}")
print(f"Energy saver: {profile.energy_saver_mode}")
```

### Perfil Power Saver
```python
# Ahorro máximo de energía
profile = manager.get_profile("power_saver")
print(f"CPU Min: {profile.cpu_min_freq} MHz")
print(f"Screen off: {profile.screen_off_timeout} min")
print(f"Disk timeout: {profile.disk_timeout} min")
```

### Perfil Ultra Low
```python
# Consumo mínimo - para servidores
profile = manager.get_profile("ultra_low")
print(f"CPU Governor: {profile.cpu_governor}")
print(f"Network throttling: {profile.network_throttle}")
```

## 🔄 Modo Adaptativo

### Habilitar Control Automático
```python
# Activar modo adaptativo
manager.enable_adaptive_mode()

# Configurar umbrales
manager.set_adaptive_thresholds(
    cpu_high=80,      # Cambiar a high_performance si CPU > 80%
    cpu_low=20,       # Cambiar a power_saver si CPU < 20%
    battery_low=15,   # Forzar power_saver si batería < 15%
    temperature_high=80  # Activar enfriamiento si temp > 80°C
)
```

### Monitoreo Adaptativo
```python
# Obtener métricas de decisión
decisions = manager.get_adaptive_decisions()
for decision in decisions:
    print(f"Trigger: {decision['trigger']}")
    print(f"Action: {decision['action']}")
    print(f"Timestamp: {decision['timestamp']}")
```

### Historial de Cambios
```python
# Ver historial de cambios de perfil
history = manager.get_profile_change_history()
for change in history:
    print(f"From: {change['from_profile']} -> To: {change['to_profile']}")
    print(f"Reason: {change['reason']}")
    print(f"Time: {change['timestamp']}")
```

## 🌡️ Monitoreo Térmico

### Estado Térmico
```python
# Obtener temperaturas del sistema
thermal_status = manager.get_thermal_status()
print(f"CPU Temperature: {thermal_status['cpu_temp']}°C")
print(f"GPU Temperature: {thermal_status['gpu_temp']}°C")
print(f"System Temperature: {thermal_status['system_temp']}°C")
print(f"Fan Speed: {thermal_status['fan_speed']} RPM")
```

### Alertas Térmicas
```python
# Configurar alertas de temperatura
manager.set_thermal_alerts(
    warning_temp=70,   # Alerta a 70°C
    critical_temp=85,  # Acción crítica a 85°C
    fan_boost_temp=75  # Aumentar ventiladores a 75°C
)
```

### Control de Ventiladores
```python
# Control manual de ventiladores
manager.set_fan_speed(80)  # 80% de velocidad máxima

# Modo automático
manager.set_fan_mode("auto")  # auto, manual, silent, performance
```

## 🔋 Monitoreo de Batería

### Estado de Batería
```python
# Información completa de batería
battery_info = manager.get_battery_info()
print(f"Level: {battery_info['percent']}%")
print(f"Status: {battery_info['status']}")  # charging, discharging, full
print(f"Time remaining: {battery_info['time_remaining']} min")
print(f"Power source: {battery_info['power_source']}")  # AC, DC, battery
```

### Optimizaciones de Batería
```python
# Activar optimizaciones de batería
manager.enable_battery_optimization()

# Configurar umbrales de batería
manager.set_battery_thresholds(
    critical_level=5,   # Acción crítica al 5%
    low_level=15,       # Modo ahorro al 15%
    full_level=95       # Notificación completa al 95%
)
```

### Historial de Batería
```python
# Obtener historial de carga/descarga
battery_history = manager.get_battery_history(hours=24)
for entry in battery_history:
    print(f"Time: {entry['timestamp']}")
    print(f"Level: {entry['level']}%")
    print(f"Status: {entry['status']}")
```

## ⚙️ Configuración Avanzada

### Perfiles Personalizados
```python
from power_management import PowerProfile

# Crear perfil personalizado
custom_profile = PowerProfile(
    name="gaming",
    cpu_governor="performance",
    cpu_max_freq=4000,
    gpu_max_freq=1500,
    screen_timeout=0,  # Nunca apagar
    sleep_timeout=0,   # Nunca dormir
    energy_saver=False
)

# Registrar perfil personalizado
manager.add_custom_profile(custom_profile)

# Aplicar perfil personalizado
manager.apply_profile("gaming")
```

### Programación de Perfiles
```python
# Programar cambios automáticos
manager.schedule_profile_change(
    profile="power_saver",
    time="18:00",  # A las 6 PM
    days=["monday", "tuesday", "wednesday", "thursday", "friday"]
)

manager.schedule_profile_change(
    profile="high_performance", 
    time="09:00",  # A las 9 AM
    days=["monday", "tuesday", "wednesday", "thursday", "friday"]
)
```

### Integración con Tareas
```python
# Cambiar perfil durante tareas específicas
manager.on_task_start("video_rendering", "high_performance")
manager.on_task_end("video_rendering", "balanced")
```

## 🔗 Integración con Otros Sistemas

### Con Notification System
```python
# Notificar cambios de perfil
manager.on_profile_change(lambda profile, reason:
    notification_manager.send_notification(
        f"Power profile changed to {profile} ({reason})",
        "info",
        ["desktop"]
    )
)
```

### Con Backup System
```python
# Ajustar perfil durante backups
backup_manager.on_backup_start(lambda:
    manager.apply_profile("balanced")  # Asegurar estabilidad
)

backup_manager.on_backup_end(lambda:
    manager.apply_profile("power_saver")  # Volver a ahorro
)
```

### Con Dashboard
```python
# Mostrar métricas en dashboard
dashboard.add_power_widget(manager)
```

## 📊 Monitoreo y Estadísticas

### Métricas de Rendimiento
```python
# Obtener estadísticas de energía
stats = manager.get_power_statistics()
print(f"Average CPU frequency: {stats['avg_cpu_freq']} MHz")
print(f"Energy consumed: {stats['energy_consumed']} Wh")
print(f"Uptime: {stats['uptime_hours']} hours")
print(f"Profile changes: {stats['profile_changes_count']}")
```

### Reportes de Eficiencia
```python
# Generar reporte de eficiencia energética
report = manager.generate_efficiency_report(days=7)
print(f"Energy efficiency: {report['efficiency_score']}%")
print(f"Power savings: {report['savings_percent']}%")
print(f"Optimal profile usage: {report['optimal_usage']}%")
```

## 🚨 Manejo de Errores

### Recuperación de Fallos
```python
# Configurar recuperación automática
manager.set_recovery_policy(
    max_retry_attempts=3,
    fallback_profile="balanced",
    error_notification=True
)
```

### Diagnóstico de Problemas
```python
# Ejecutar diagnóstico del sistema de energía
diagnostic = manager.run_power_diagnostic()
print("Diagnostic Results:")
for issue in diagnostic['issues']:
    print(f"- {issue['description']}: {issue['severity']}")

for recommendation in diagnostic['recommendations']:
    print(f"✓ {recommendation}")
```

## 📚 API Reference

### Clase PowerManager

#### Métodos Principales
- `apply_profile(profile_name)`: Aplica un perfil de energía
- `get_power_status()`: Obtiene estado actual del sistema
- `enable_adaptive_mode()`: Activa modo adaptativo
- `get_thermal_status()`: Obtiene estado térmico
- `get_battery_info()`: Obtiene información de batería

#### Métodos de Configuración
- `set_adaptive_thresholds(**kwargs)`: Configura umbrales adaptativos
- `set_thermal_alerts(**kwargs)`: Configura alertas térmicas
- `set_battery_thresholds(**kwargs)`: Configura umbrales de batería
- `add_custom_profile(profile)`: Agrega perfil personalizado

### Clase PowerProfile

#### Atributos Principales
- `name`: Nombre del perfil
- `cpu_governor`: Gobernador de CPU
- `cpu_min_freq`: Frecuencia mínima de CPU
- `cpu_max_freq`: Frecuencia máxima de CPU
- `screen_timeout`: Timeout de pantalla (minutos)
- `sleep_timeout`: Timeout de suspensión (minutos)
- `energy_saver`: Modo ahorro de energía

## 🔍 Ejemplos Avanzados

### Sistema de Gestión Energética Completo
```python
from power_management import PowerManager, PowerProfile
import time

class EnergyManager:
    def __init__(self):
        self.power = PowerManager()
        self.setup_profiles()
        self.setup_adaptive_rules()
    
    def setup_profiles(self):
        """Configura perfiles optimizados"""
        
        # Perfil para desarrollo
        dev_profile = PowerProfile(
            name="development",
            cpu_governor="performance",
            cpu_min_freq=2000,
            cpu_max_freq=3500,
            screen_timeout=30,
            sleep_timeout=60,
            energy_saver=False
        )
        
        # Perfil para gaming
        gaming_profile = PowerProfile(
            name="gaming",
            cpu_governor="performance", 
            cpu_min_freq=3000,
            cpu_max_freq=4000,
            gpu_max_freq=1800,
            screen_timeout=0,
            sleep_timeout=0,
            energy_saver=False
        )
        
        self.power.add_custom_profile(dev_profile)
        self.power.add_custom_profile(gaming_profile)
    
    def setup_adaptive_rules(self):
        """Configura reglas adaptativas inteligentes"""
        
        self.power.set_adaptive_thresholds(
            cpu_high=75,      # High performance si CPU > 75%
            cpu_medium=50,    # Balanced si CPU entre 25-75%
            cpu_low=25,       # Power saver si CPU < 25%
            battery_critical=10,  # Ultra low si batería < 10%
            temperature_high=80   # Activar enfriamiento forzado
        )
        
        # Programar cambios diarios
        self.power.schedule_profile_change("power_saver", "18:00", 
                                         ["monday", "tuesday", "wednesday", "thursday", "friday"])
        self.power.schedule_profile_change("balanced", "09:00",
                                         ["monday", "tuesday", "wednesday", "thursday", "friday"])
    
    def monitor_and_optimize(self):
        """Loop principal de monitoreo y optimización"""
        while True:
            try:
                # Obtener métricas actuales
                status = self.power.get_power_status()
                
                # Aplicar lógica adicional si es necesario
                if status['battery_percent'] < 20 and status['power_source'] == 'battery':
                    self.power.apply_profile('power_saver')
                    print("🔋 Batería baja - cambiando a modo ahorro")
                
                # Verificar temperatura
                thermal = self.power.get_thermal_status()
                if thermal['cpu_temp'] > 85:
                    print("🔥 Temperatura alta - activando enfriamiento")
                    self.power.set_fan_mode('performance')
                
                time.sleep(30)  # Monitorear cada 30 segundos
                
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                time.sleep(60)

# Uso
energy_manager = EnergyManager()
energy_manager.power.enable_adaptive_mode()
energy_manager.monitor_and_optimize()
```

Este sistema proporciona control completo y inteligente del consumo energético, adaptándose automáticamente a las necesidades del sistema y del usuario.</content>
<parameter name="filePath">c:\Users\DELL\Desktop\BackendBot\docs\POWER_MANAGEMENT.md