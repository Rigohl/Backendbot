"""
Demo del Monitor Worker
=======================

Demostración del funcionamiento del MonitorWorker.
"""

import os
import sys
import time

# Agregar el directorio backendbot al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backendbot"))

from backendbot.packages.bots.monitor_worker import MonitorWorker


def demo_monitor_worker():
    """Demostración del Monitor Worker."""
    print("🚀 Iniciando demo del Monitor Worker...")
    print("=" * 50)

    # Crear instancia del Monitor Worker
    monitor = MonitorWorker(bot_id="demo-monitor", name="Demo Monitor Worker")

    print("📊 Configuración del Monitor Worker:")
    print(f"   - ID: {monitor.bot_id}")
    print(f"   - Nombre: {monitor.name}")
    print(f"   - Intervalo: {monitor.monitoring_interval}s")
    print(f"   - Umbrales: {monitor.alert_thresholds}")
    print()

    # Callback para alertas
    def alert_callback(alert):
        print(f"🚨 ALERTA RECIBIDA: {alert['message']}")

    monitor.add_alert_callback(alert_callback)

    print("▶️  Iniciando Monitor Worker...")
    monitor.start()

    print("⏳ Monitoreando sistema por 10 segundos...")
    for i in range(10):
        time.sleep(1)
        metrics = monitor.get_current_metrics()
        if metrics:
            print(
                ".1f"
                f"Mem: {metrics['memory_usage']:.1f}%, "
                f"Disk: {metrics['disk_usage']:.1f}%"
            )
        else:
            print(f"⏳ Esperando métricas... ({i+1}/10)")

    print()
    print("📈 Historial de métricas:")
    history = monitor.get_metrics_history(limit=3)
    for i, metric in enumerate(history):
        print(
            f"   {i+1}. CPU: {metric['cpu_usage']:.1f}%, "
            f"Mem: {metric['memory_usage']:.1f}%, "
            f"Disk: {metric['disk_usage']:.1f}%"
        )

    print()
    print("🔔 Alertas generadas:")
    alerts = monitor.get_alerts()
    if alerts:
        for alert in alerts:
            print(f"   - {alert['type'].upper()}: {alert['message']}")
    else:
        print("   (Ninguna alerta generada)")

    print()
    print("🖥️  Información del sistema:")
    system_info = monitor.get_system_info()
    for key, value in system_info.items():
        if isinstance(value, int) and value > 1000000:  # Bytes a MB/GB
            if value > 1000000000:
                print(f"   - {key}: {value/1000000000:.1f} GB")
            else:
                print(f"   - {key}: {value/1000000:.1f} MB")
        else:
            print(f"   - {key}: {value}")

    print()
    print("⏹️  Deteniendo Monitor Worker...")
    monitor.stop()

    print("✅ Demo completada exitosamente!")
    print("=" * 50)


if __name__ == "__main__":
    demo_monitor_worker()
