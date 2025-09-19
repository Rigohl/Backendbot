#!/usr/bin/env python3
"""
Demo completa del GuardianWorker - Sistema de Seguridad BackendBot

Esta demo muestra todas las capacidades de seguridad del GuardianWorker:
- Detección de amenazas por extensión
- Análisis de patrones (regex y simple)
- Verificación de integridad de archivos (SHA256)
- Sistema de alertas y callbacks
- Monitoreo en background
- Estadísticas de seguridad
- Manejo de archivos corruptos y permisos
"""

import os
import tempfile
import time
from pathlib import Path

# Importaciones del proyecto
from backendbot.packages.bots.guardian_worker import GuardianWorker
from backendbot.packages.models.models import ThreatLevel


def create_test_files(base_dir: Path):
    """Crear archivos de prueba con diferentes tipos de contenido."""
    print("🏗️  Creando archivos de prueba...")

    # Archivo seguro
    safe_file = base_dir / "documento_seguro.txt"
    safe_file.write_text("Este es un documento seguro sin amenazas.")

    # Archivo con extensión sospechosa
    suspicious_file = base_dir / "script_malicioso.exe"
    suspicious_file.write_text("Contenido sospechoso")

    # Archivo con patrón de amenaza
    threat_file = base_dir / "archivo_peligroso.txt"
    threat_file.write_text("Contiene malware y virus peligroso")

    # Archivo grande (para testing de rendimiento)
    large_file = base_dir / "archivo_grande.txt"
    large_content = "A" * 1000000  # 1MB de contenido
    large_file.write_text(large_content)

    # Archivo corrupto (simulado)
    corrupt_file = base_dir / "archivo_corrupto.txt"
    try:
        corrupt_file.write_text("Contenido normal")
        # Simular corrupción cambiando permisos o contenido
        os.chmod(corrupt_file, 0o000)  # Sin permisos
    except:
        pass  # En Windows puede fallar

    print(f"✅ Archivos creados en: {base_dir}")
    return safe_file, suspicious_file, threat_file, large_file, corrupt_file


def setup_guardian_worker():
    """Configurar el GuardianWorker con patrones de seguridad."""
    print("\n🔧 Configurando GuardianWorker...")

    # Configuración de seguridad
    config = {
        'monitored_paths': ['.'],
        'excluded_paths': [
            r'\.git/',
            r'__pycache__/',
            r'node_modules/',
            r'\.venv/',
            r'venv/',
        ],
        'threat_patterns': [
            r'malware|virus|trojan',  # Regex pattern
            'peligroso',  # Simple pattern
        ],
        'suspicious_extensions': {
            '.exe', '.bat', '.cmd', '.scr', '.pif', '.com',
            '.vbs', '.js', '.jar', '.dll', '.sys', '.drv'
        },
        'max_file_size_alert': 1024 * 1024,  # 1MB
        'integrity_check_interval': 300,  # 5 minutos
        'execution_interval': 60,  # 1 minuto
        'enable_real_time_monitoring': True,
        'log_security_events': True,
        'auto_quarantine': False,
        'alert_on_suspicious': True,
    }

    # Crear GuardianWorker con bot_id y name
    guardian = GuardianWorker(bot_id="guardian_demo", name="Guardian Worker Demo")

    # Validar y aplicar configuración
    if guardian.validate_config(config):
        guardian.config = config
        guardian.on_config_updated()  # Aplicar configuración
        print("✅ Configuración validada y aplicada")
    else:
        print("❌ Error en validación de configuración")
        return None, [], []

    # Configurar callbacks
    alerts_received = []
    security_events = []

    def alert_callback(alert):
        alerts_received.append(alert)
        print(f"🚨 ALERTA: {alert.threat_level.name} - {alert.file_path}")
        print(f"   Detalles: {alert.details}")

    def security_callback(event):
        security_events.append(event)
        print(f"🔒 EVENTO: {event.event_type} - {event.source}")

    guardian.add_alert_callback(alert_callback)
    guardian.add_security_callback(security_callback)

    print("✅ GuardianWorker configurado con callbacks")
    return guardian, alerts_received, security_events


def demo_security_scanning(guardian: GuardianWorker, test_dir: Path):
    """Demostrar escaneo de seguridad básico."""
    print("\n🔍 Ejecutando escaneo de seguridad básico...")

    # Configurar ruta monitoreada al directorio de prueba
    guardian.config['monitored_paths'] = [str(test_dir)]
    guardian.on_config_updated()

    # Ejecutar escaneo
    start_time = time.time()
    results = guardian.execute_task()
    end_time = time.time()

    print(f"Tiempo de escaneo: {end_time - start_time:.2f}s")
    print(f"📊 Resultados del escaneo: {results}")

    # Mostrar estadísticas
    stats = guardian.get_security_stats()
    print("📈 Estadísticas de seguridad:")
    for key, value in stats.items():
        print(f"   {key}: {value}")


def demo_integrity_check(guardian: GuardianWorker, safe_file: Path):
    """Demostrar verificación de integridad."""
    print("\n🔐 Verificando integridad de archivos...")
    # Calcular hash inicial
    initial_hash = guardian._calculate_file_hash(safe_file)
    print(f"   Hash inicial: {initial_hash[:16]}...")

    # Verificar integridad (debería pasar)
    integrity_ok = guardian._perform_integrity_check()
    print(f"   Verificación de integridad: {'✅ OK' if integrity_ok else '❌ FALLÓ'}")

    # Modificar archivo y verificar nuevamente
    original_content = safe_file.read_text()
    safe_file.write_text(original_content + " - modificado")

    integrity_ok_after = guardian._perform_integrity_check()
    print(f"   Verificación después de modificación: {'✅ OK' if integrity_ok_after else '❌ FALLÓ'}")

    # Restaurar contenido original
    safe_file.write_text(original_content)


def demo_background_execution(guardian: GuardianWorker):
    """Demostrar ejecución en background."""
    print("\n⚡ Iniciando monitoreo en background...")
    if guardian.should_run_in_background():
        print("   Background execution: ✅ Habilitado")

        # Simular algunas ejecuciones periódicas
        for i in range(3):
            print(f"   Ejecutando tarea periódica #{i+1}...")
            guardian.execute_periodic_task()
            time.sleep(0.1)  # Pequeña pausa

        print("   ✅ Tareas en background completadas")
    else:
        print("   ❌ Background execution no disponible")


def demo_error_handling(guardian: GuardianWorker, corrupt_file: Path):
    """Demostrar manejo de errores."""
    print("\n🛡️  Probando manejo de errores...")
    try:
        # Intentar escanear archivo corrupto
        guardian._scan_file_for_threats(corrupt_file)
        print("   ✅ Archivo corrupto manejado correctamente")
    except Exception as e:
        print(f"   ⚠️  Error esperado al manejar archivo corrupto: {type(e).__name__}")

    # Limpiar datos de seguridad
    guardian.clear_security_data()
    print("   🧹 Datos de seguridad limpiados")


def demo_threat_levels():
    """Mostrar niveles de amenaza disponibles."""
    print("\n📊 Niveles de amenaza disponibles:")
    for level in ThreatLevel:
        print(f"   {level.name}: {level.value}")


def main():
    """Función principal de la demo."""
    print("🚀 DEMO COMPLETA DEL GUARDIAN WORKER - BACKEND BOT")
    print("=" * 60)

    # Crear directorio temporal para pruebas
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)

        try:
            # Crear archivos de prueba
            safe_file, suspicious_file, threat_file, large_file, corrupt_file = create_test_files(test_dir)

            # Configurar GuardianWorker
            guardian, alerts_received, security_events = setup_guardian_worker()

            # Ejecutar demos
            demo_security_scanning(guardian, test_dir)
            demo_integrity_check(guardian, safe_file)
            demo_background_execution(guardian)
            demo_error_handling(guardian, corrupt_file)
            demo_threat_levels()

            # Resumen final
            print("\n🎉 RESUMEN DE LA DEMO")
            print("=" * 60)
            print(f"📁 Directorio de prueba: {test_dir}")
            print(f"🚨 Alertas generadas: {len(alerts_received)}")
            print(f"🔒 Eventos de seguridad: {len(security_events)}")

            final_stats = guardian.get_security_stats()
            print("📈 Estadísticas finales:")
            for key, value in final_stats.items():
                print(f"   {key}: {value}")

            print("\n✅ Demo completada exitosamente!")
            print("El GuardianWorker está listo para proteger tu sistema BackendBot.")

        except Exception as e:
            print(f"❌ Error durante la demo: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()