# 📊 Dashboard Interactivo

## 📋 Descripción General

El Dashboard Interactivo de BackendBot proporciona una interfaz gráfica completa para monitoreo en tiempo real, control de sistemas y visualización de métricas con widgets personalizables y temas adaptativos.

## 🚀 Características Principales

- **Widgets en Tiempo Real**: CPU, RAM, disco, red y procesos
- **Controles Directos**: Botones para acciones rápidas
- **Gráficos Históricos**: Tendencias de rendimiento a lo largo del tiempo
- **Tema Personalizable**: Interfaz adaptable a preferencias del usuario
- **Alertas Visuales**: Indicadores de estado del sistema
- **Múltiples Vistas**: Paneles especializados por función
- **Integración Completa**: Conecta todos los sistemas de BackendBot

## 📁 Estructura del Sistema

```
dashboard/
├── __init__.py
├── main_dashboard.py            # Ventana principal del dashboard
├── dashboard_controller.py      # Controlador principal
├── widgets/                     # Componentes de widgets
│   ├── __init__.py
│   ├── system_monitor_widget.py # Widget de monitoreo sistema
│   ├── process_widget.py        # Widget de procesos
│   ├── network_widget.py        # Widget de red
│   ├── storage_widget.py        # Widget de almacenamiento
│   ├── power_widget.py          # Widget de energía
│   ├── backup_widget.py         # Widget de backups
│   └── notification_widget.py   # Widget de notificaciones
├── themes/                      # Temas y estilos
│   ├── __init__.py
│   ├── light_theme.py          # Tema claro
│   ├── dark_theme.py           # Tema oscuro
│   └── custom_theme.py         # Tema personalizado
├── views/                       # Vistas especializadas
│   ├── __init__.py
│   ├── system_view.py          # Vista de sistema
│   ├── performance_view.py     # Vista de rendimiento
│   ├── network_view.py         # Vista de red
│   └── backup_view.py          # Vista de backups
└── utils/                       # Utilidades
    ├── __init__.py
    ├── chart_utils.py          # Utilidades de gráficos
    └── data_formatter.py       # Formateo de datos
```

## 🛠️ Uso Básico

### Inicialización
```python
from dashboard import MainDashboard

# Crear y mostrar dashboard
dashboard = MainDashboard()
dashboard.show()
```

### Ejecutar Dashboard
```bash
# Desde el entorno virtual
python dashboard.py
```

### Personalización Básica
```python
# Configurar tema
dashboard.set_theme("dark")

# Configurar actualización automática
dashboard.set_update_interval(2000)  # 2 segundos

# Mostrar/ocultar widgets
dashboard.show_widget("cpu_monitor", True)
dashboard.show_widget("memory_monitor", True)
dashboard.show_widget("network_monitor", False)
```

## 🎯 Widgets Principales

### Widget de Monitoreo del Sistema
```python
from dashboard.widgets import SystemMonitorWidget

# Crear widget de sistema
system_widget = SystemMonitorWidget()
system_widget.set_metrics(["cpu", "memory", "disk", "network"])
system_widget.set_update_interval(1000)  # 1 segundo

# Agregar al dashboard
dashboard.add_widget(system_widget, position=(0, 0), size=(400, 300))
```

### Widget de Procesos
```python
from dashboard.widgets import ProcessWidget

# Widget de procesos activos
process_widget = ProcessWidget()
process_widget.set_sort_by("cpu_percent")  # Ordenar por uso de CPU
process_widget.set_max_processes(20)       # Mostrar top 20
process_widget.enable_kill_buttons(True)   # Habilitar botones de terminar

dashboard.add_widget(process_widget, position=(400, 0), size=(400, 300))
```

### Widget de Red
```python
from dashboard.widgets import NetworkWidget

# Widget de monitoreo de red
network_widget = NetworkWidget()
network_widget.set_interfaces(["Ethernet", "Wi-Fi"])  # Interfaces a monitorear
network_widget.show_bandwidth_history(True)           # Mostrar historial
network_widget.set_alert_threshold(100 * 1024 * 1024) # Alerta > 100MB/s

dashboard.add_widget(network_widget, position=(0, 300), size=(400, 300))
```

### Widget de Energía
```python
from dashboard.widgets import PowerWidget

# Widget de gestión de energía
power_widget = PowerWidget()
power_widget.show_battery_info(True)
power_widget.show_power_profiles(True)
power_widget.enable_profile_buttons(True)

dashboard.add_widget(power_widget, position=(400, 300), size=(400, 300))
```

## 🎨 Temas y Personalización

### Temas Predefinidos
```python
# Tema oscuro
dashboard.set_theme("dark")

# Tema claro
dashboard.set_theme("light")

# Tema personalizado
custom_theme = {
    "background_color": "#2b2b2b",
    "text_color": "#ffffff",
    "accent_color": "#007acc",
    "warning_color": "#ffcc00",
    "error_color": "#ff4444"
}
dashboard.set_custom_theme(custom_theme)
```

### Personalización de Widgets
```python
# Personalizar colores de widget
cpu_widget.set_colors({
    "background": "#1e1e1e",
    "text": "#ffffff",
    "chart_background": "#2d2d2d",
    "chart_line": "#007acc"
})

# Configurar fuentes
cpu_widget.set_font("Segoe UI", 10)

# Configurar márgenes y espaciado
cpu_widget.set_padding(10)
cpu_widget.set_spacing(5)
```

## 📊 Gráficos y Visualizaciones

### Gráfico de Rendimiento
```python
from dashboard.utils import ChartUtils

# Crear gráfico de CPU
cpu_chart = ChartUtils.create_line_chart(
    data_points=cpu_history,
    title="CPU Usage History",
    x_label="Time",
    y_label="Usage %",
    color="#007acc",
    show_grid=True
)

# Agregar al widget
cpu_widget.set_chart(cpu_chart)
```

### Gráfico de Red
```python
# Gráfico de ancho de banda
bandwidth_chart = ChartUtils.create_area_chart(
    data_points=network_history,
    title="Network Bandwidth",
    x_label="Time", 
    y_label="MB/s",
    colors=["#00ff00", "#ff0000"],  # Download/Upload
    fill_opacity=0.3
)

network_widget.set_chart(bandwidth_chart)
```

### Gráfico de Almacenamiento
```python
# Gráfico de uso de disco
disk_chart = ChartUtils.create_pie_chart(
    data_points=disk_usage,
    title="Disk Usage",
    colors=["#007acc", "#ffcc00", "#ff4444", "#00ff00"],
    show_percentages=True
)

storage_widget.set_chart(disk_chart)
```

## 🔄 Vistas Especializadas

### Vista de Sistema
```python
from dashboard.views import SystemView

# Vista completa del sistema
system_view = SystemView()
system_view.add_widget(SystemMonitorWidget())
system_view.add_widget(PowerWidget())
system_view.add_widget(NotificationWidget())

# Mostrar vista
dashboard.show_view(system_view)
```

### Vista de Rendimiento
```python
from dashboard.views import PerformanceView

# Vista enfocada en rendimiento
perf_view = PerformanceView()
perf_view.add_cpu_monitor()
perf_view.add_memory_monitor()
perf_view.add_disk_monitor()
perf_view.add_network_monitor()

dashboard.show_view(perf_view)
```

### Vista de Backups
```python
from dashboard.views import BackupView

# Vista de gestión de backups
backup_view = BackupView()
backup_view.show_backup_list()
backup_view.show_backup_progress()
backup_view.enable_backup_controls()

dashboard.show_view(backup_view)
```

## 🚨 Alertas y Notificaciones

### Configuración de Alertas
```python
# Configurar alertas visuales
dashboard.set_alert_config({
    "cpu_threshold": 80,        # Alerta CPU > 80%
    "memory_threshold": 85,     # Alerta memoria > 85%
    "disk_threshold": 90,       # Alerta disco > 90%
    "network_threshold": 100,   # Alerta red > 100MB/s
    "alert_duration": 5000      # Duración de alerta en ms
})

# Tipos de alertas
dashboard.set_alert_types({
    "info": {"color": "#007acc", "icon": "ℹ️"},
    "warning": {"color": "#ffcc00", "icon": "⚠️"},
    "error": {"color": "#ff4444", "icon": "❌"},
    "success": {"color": "#00ff00", "icon": "✅"}
})
```

### Notificaciones en Dashboard
```python
# Mostrar notificación
dashboard.show_notification(
    message="CPU usage above 80%",
    type="warning",
    duration=5000
)

# Notificación con acción
dashboard.show_notification(
    message="Backup completed successfully",
    type="success",
    action_button="View Details",
    action_callback=lambda: show_backup_details()
)
```

## ⚙️ Configuración Avanzada

### Configuración de Layout
```python
# Configurar layout de widgets
layout_config = {
    "grid_size": (800, 600),
    "widget_margins": 10,
    "auto_arrange": True,
    "snap_to_grid": True
}
dashboard.set_layout_config(layout_config)

# Guardar/cargar layout
dashboard.save_layout("my_layout.json")
dashboard.load_layout("my_layout.json")
```

### Configuración de Rendimiento
```python
# Optimizar para rendimiento
performance_config = {
    "update_interval": 1000,      # ms
    "max_data_points": 100,       # Puntos en gráficos
    "enable_caching": True,       # Cache de datos
    "background_updates": True,   # Actualizaciones en background
    "low_power_mode": False       # Modo bajo consumo
}
dashboard.set_performance_config(performance_config)
```

## 🔗 Integración con Otros Sistemas

### Con Notification System
```python
# Mostrar notificaciones del sistema
notification_widget = NotificationWidget()
notification_widget.connect_to_notification_manager(notification_manager)

# Mostrar alertas del sistema
dashboard.show_system_alerts(notification_manager)
```

### Con Power Management
```python
# Control de energía desde dashboard
power_widget = PowerWidget()
power_widget.connect_to_power_manager(power_manager)

# Mostrar estado de batería
dashboard.add_battery_indicator(power_manager)
```

### Con Backup System
```python
# Gestión de backups desde dashboard
backup_widget = BackupWidget()
backup_widget.connect_to_backup_manager(backup_manager)

# Mostrar progreso de backups
dashboard.show_backup_progress(backup_manager)
```

## 📊 Monitoreo y Estadísticas

### Métricas del Dashboard
```python
# Obtener estadísticas de uso
stats = dashboard.get_usage_statistics()
print(f"Widgets activos: {stats['active_widgets']}")
print(f"Actualizaciones por segundo: {stats['updates_per_second']}")
print(f"Memoria usada: {stats['memory_usage_mb']} MB")
```

### Rendimiento de Widgets
```python
# Monitorear rendimiento de widgets
performance = dashboard.get_widget_performance()
for widget_name, perf in performance.items():
    print(f"{widget_name}: {perf['update_time_ms']}ms avg")
```

## 🚨 Manejo de Errores

### Recuperación de Errores
```python
# Configurar manejo de errores
dashboard.set_error_handling({
    "auto_restart_widgets": True,
    "show_error_notifications": True,
    "log_errors": True,
    "error_log_file": "dashboard_errors.log"
})
```

### Diagnóstico
```python
# Ejecutar diagnóstico del dashboard
diagnostic = dashboard.run_diagnostic()
print("Dashboard Diagnostic:")
for issue in diagnostic['issues']:
    print(f"- {issue['component']}: {issue['description']}")

for recommendation in diagnostic['recommendations']:
    print(f"✓ {recommendation}")
```

## 📚 API Reference

### Clase MainDashboard

#### Métodos Principales
- `show()`: Muestra el dashboard
- `add_widget(widget, position, size)`: Agrega widget
- `remove_widget(widget_name)`: Remueve widget
- `set_theme(theme_name)`: Cambia tema
- `show_view(view)`: Muestra vista específica

#### Métodos de Configuración
- `set_update_interval(ms)`: Configura intervalo de actualización
- `set_layout_config(config)`: Configura layout
- `set_performance_config(config)`: Configura rendimiento
- `save_layout(filename)`: Guarda layout
- `load_layout(filename)`: Carga layout

### Widgets Disponibles
- `SystemMonitorWidget`: Monitoreo general del sistema
- `ProcessWidget`: Gestión de procesos
- `NetworkWidget`: Monitoreo de red
- `StorageWidget`: Información de almacenamiento
- `PowerWidget`: Gestión de energía
- `BackupWidget`: Control de backups
- `NotificationWidget`: Centro de notificaciones

## 🔍 Ejemplos Avanzados

### Dashboard Empresarial Completo
```python
from dashboard import MainDashboard
from dashboard.widgets import *
from dashboard.views import *

class EnterpriseDashboard:
    def __init__(self):
        self.dashboard = MainDashboard()
        self.setup_enterprise_layout()
        self.setup_monitoring()
        self.setup_alerts()
    
    def setup_enterprise_layout(self):
        """Configura layout para entorno empresarial"""
        
        # Configurar tema profesional
        self.dashboard.set_theme("dark")
        
        # Crear vista principal
        main_view = SystemView()
        
        # Widget de monitoreo del sistema
        system_monitor = SystemMonitorWidget()
        system_monitor.set_metrics(["cpu", "memory", "disk", "network"])
        system_monitor.set_update_interval(2000)
        main_view.add_widget(system_monitor, (0, 0), (600, 400))
        
        # Widget de procesos críticos
        process_widget = ProcessWidget()
        process_widget.set_filter(["sqlserver.exe", "apache.exe", "nginx.exe"])
        process_widget.enable_restart_buttons(True)
        main_view.add_widget(process_widget, (600, 0), (400, 400))
        
        # Widget de red empresarial
        network_widget = NetworkWidget()
        network_widget.set_interfaces(["Ethernet", "VPN"])
        network_widget.show_bandwidth_history(True)
        network_widget.set_alert_threshold(500 * 1024 * 1024)  # 500MB/s
        main_view.add_widget(network_widget, (0, 400), (500, 300))
        
        # Widget de almacenamiento
        storage_widget = StorageWidget()
        storage_widget.set_paths(["C:/", "D:/", "E:/"])
        storage_widget.show_usage_trends(True)
        main_view.add_widget(storage_widget, (500, 400), (500, 300))
        
        # Vista de backups
        backup_view = BackupView()
        backup_widget = BackupWidget()
        backup_widget.connect_to_backup_manager(self.backup_manager)
        backup_view.add_widget(backup_widget, (0, 0), (1000, 600))
        
        # Vista de energía
        power_view = SystemView()
        power_widget = PowerWidget()
        power_widget.connect_to_power_manager(self.power_manager)
        power_view.add_widget(power_widget, (0, 0), (800, 600))
        
        # Agregar vistas al dashboard
        self.dashboard.add_view("main", main_view)
        self.dashboard.add_view("backups", backup_view)
        self.dashboard.add_view("power", power_view)
        
        # Configurar navegación
        self.dashboard.set_navigation([
            {"name": "Sistema", "view": "main"},
            {"name": "Backups", "view": "backups"},
            {"name": "Energía", "view": "power"}
        ])
    
    def setup_monitoring(self):
        """Configura monitoreo avanzado"""
        
        # Configurar métricas críticas
        self.dashboard.set_critical_metrics({
            "cpu_threshold": 80,
            "memory_threshold": 85,
            "disk_threshold": 90,
            "network_threshold": 100 * 1024 * 1024
        })
        
        # Configurar logging
        self.dashboard.enable_logging("enterprise_dashboard.log")
        
        # Configurar exportación de datos
        self.dashboard.enable_data_export(
            format="json",
            interval=3600000,  # Cada hora
            destination="C:/Monitoring/Exports"
        )
    
    def setup_alerts(self):
        """Configura sistema de alertas"""
        
        # Alertas críticas
        self.dashboard.set_alert_rules([
            {
                "condition": "cpu_percent > 90",
                "message": "🚨 CPU CRÍTICA: Uso por encima del 90%",
                "type": "error",
                "actions": ["notify_admin", "log_incident"]
            },
            {
                "condition": "memory_percent > 95",
                "message": "🚨 MEMORIA CRÍTICA: Uso por encima del 95%",
                "type": "error", 
                "actions": ["notify_admin", "auto_cleanup"]
            },
            {
                "condition": "disk_percent > 95",
                "message": "🚨 DISCO CRÍTICO: Espacio por debajo del 5%",
                "type": "error",
                "actions": ["notify_admin", "cleanup_temp"]
            }
        ])
        
        # Configurar notificaciones
        self.dashboard.configure_notifications({
            "admin_email": "admin@company.com",
            "slack_webhook": "https://hooks.slack.com/...",
            "sms_enabled": True,
            "sms_numbers": ["+1234567890"]
        })
    
    def start_monitoring(self):
        """Inicia el monitoreo del sistema"""
        self.dashboard.show_view("main")
        self.dashboard.start_auto_refresh(5000)  # Actualizar cada 5 segundos
        
        # Iniciar monitoreo en background
        self.dashboard.start_background_monitoring()
    
    def generate_report(self):
        """Genera reporte ejecutivo"""
        report_data = self.dashboard.get_system_report()
        
        report = f"""
📊 Reporte Ejecutivo - BackendBot Dashboard
==========================================

📈 Rendimiento General
- CPU Promedio: {report_data['avg_cpu']}%
- Memoria Usada: {report_data['avg_memory']}%
- Disco Usado: {report_data['avg_disk']}%
- Red: {report_data['avg_network']} MB/s

⚠️ Alertas del Periodo
- Críticas: {report_data['critical_alerts']}
- Advertencias: {report_data['warning_alerts']}
- Información: {report_data['info_alerts']}

💾 Estado de Backups
- Último Backup: {report_data['last_backup']}
- Estado: {report_data['backup_status']}
- Cobertura: {report_data['backup_coverage']}%

🔋 Estado de Energía
- Perfil Actual: {report_data['power_profile']}
- Batería: {report_data['battery_level']}%
- Eficiencia: {report_data['power_efficiency']}%

Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return report

# Uso del dashboard empresarial
enterprise_dash = EnterpriseDashboard()
enterprise_dash.start_monitoring()

# Generar reporte semanal
print(enterprise_dash.generate_report())
```

Este dashboard proporciona una solución completa de monitoreo y control para entornos empresariales con visualizaciones avanzadas, alertas inteligentes y capacidades de reporting ejecutivo.</content>
<parameter name="filePath">c:\Users\DELL\Desktop\BackendBot\docs\DASHBOARD_SYSTEM.md