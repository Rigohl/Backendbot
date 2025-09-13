#!/usr/bin/env python3
"""
Script de prueba para características avanzadas de Railway

Este script verifica que todos los componentes de Railway estén funcionando correctamente.
"""

import asyncio
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from backendbot.railway_integration import railway, init_railway
from backendbot.cache import cache
from backendbot.monitor import monitor
from backendbot.cron_jobs import cron_jobs
from backendbot.railway_db import railway_db

async def test_cache():
    """Probar funcionalidades del cache Redis"""
    print("🧪 Probando Redis Cache...")

    if not cache.is_available():
        print("❌ Redis no disponible")
        return False

    try:
        # Probar cache de métricas
        test_metric = {'cpu': 45.2, 'memory': 67.8}
        cache.set_metric('test_metric', test_metric, ttl=60)
        retrieved = cache.get_metric('test_metric')

        if retrieved != test_metric:
            print("❌ Error en cache de métricas")
            return False

        # Probar cache de IA
        cache.cache_ai_response('test query', 'test response', ttl=60)
        response = cache.get_ai_response('test query')

        if response != 'test response':
            print("❌ Error en cache de IA")
            return False

        # Probar rate limiting
        for i in range(5):
            allowed = cache.set_rate_limit('test_user', max_requests=10)
            if not allowed:
                print("❌ Error en rate limiting")
                return False

        print("✅ Redis Cache funcionando correctamente")
        return True

    except Exception as e:
        print(f"❌ Error probando cache: {e}")
        return False

async def test_database():
    """Probar funcionalidades de Railway PostgreSQL"""
    print("🧪 Probando Railway PostgreSQL...")

    try:
        if not await railway_db.connect():
            print("❌ No se pudo conectar a PostgreSQL")
            return False

        # Probar guardar métricas
        test_data = {'test': 'data', 'timestamp': '2024-01-01'}
        await railway_db.save_metrics('test_metric', test_data)

        # Probar obtener métricas
        metrics = await railway_db.get_recent_metrics('test_metric', limit=1)
        if not metrics:
            print("❌ Error obteniendo métricas")
            return False

        # Probar estadísticas
        stats = await railway_db.get_database_stats()
        if not stats:
            print("❌ Error obteniendo estadísticas de BD")
            return False

        print("✅ Railway PostgreSQL funcionando correctamente")
        return True

    except Exception as e:
        print(f"❌ Error probando base de datos: {e}")
        return False
    finally:
        await railway_db.disconnect()

async def test_monitoring():
    """Probar funcionalidades de monitoreo"""
    print("🧪 Probando monitoreo del sistema...")

    try:
        # Probar recopilación de métricas
        metrics = await monitor.collect_system_metrics()
        if not metrics:
            print("❌ Error recopilando métricas")
            return False

        # Verificar métricas requeridas
        required_keys = ['cpu_percent', 'memory', 'disk', 'network']
        for key in required_keys:
            if key not in metrics:
                print(f"❌ Métrica faltante: {key}")
                return False

        # Probar health check
        health = await monitor.create_health_check_endpoint()
        if health.get('status') not in ['healthy', 'critical']:
            print("❌ Error en health check")
            return False

        print("✅ Monitoreo del sistema funcionando correctamente")
        return True

    except Exception as e:
        print(f"❌ Error probando monitoreo: {e}")
        return False

async def test_cron_jobs():
    """Probar funcionalidades de cron jobs"""
    print("🧪 Probando cron jobs...")

    try:
        # Verificar que el scheduler esté corriendo
        if not cron_jobs.scheduler.running:
            print("❌ Scheduler no está corriendo")
            return False

        # Obtener estado de jobs
        status = cron_jobs.get_job_status()
        if not isinstance(status, dict):
            print("❌ Error obteniendo estado de jobs")
            return False

        # Verificar jobs por defecto
        expected_jobs = ['cleanup_logs', 'backup_database', 'optimize_performance',
                        'update_cache_stats', 'health_check', 'maintenance_window']

        for job_name in expected_jobs:
            if job_name not in status:
                print(f"❌ Job faltante: {job_name}")
                return False

        print("✅ Cron jobs funcionando correctamente")
        return True

    except Exception as e:
        print(f"❌ Error probando cron jobs: {e}")
        return False

async def test_railway_integration():
    """Probar integración completa de Railway"""
    print("🧪 Probando integración completa de Railway...")

    try:
        # Obtener estado del sistema
        status = await railway.get_system_status()
        if not status:
            print("❌ Error obteniendo estado del sistema")
            return False

        # Verificar componentes
        if 'system_metrics' not in status:
            print("❌ Métricas del sistema faltantes")
            return False

        if 'cache_stats' not in status:
            print("❌ Estadísticas del cache faltantes")
            return False

        if 'database_stats' not in status:
            print("❌ Estadísticas de BD faltantes")
            return False

        print("✅ Integración completa de Railway funcionando correctamente")
        return True

    except Exception as e:
        print(f"❌ Error probando integración: {e}")
        return False

async def run_all_tests():
    """Ejecutar todas las pruebas"""
    print("🚀 Iniciando pruebas de características avanzadas de Railway\n")

    # Inicializar Railway
    print("📦 Inicializando Railway...")
    if not await init_railway():
        print("❌ Error inicializando Railway")
        return False

    print("✅ Railway inicializado correctamente\n")

    # Ejecutar pruebas
    tests = [
        ("Cache Redis", test_cache),
        ("PostgreSQL", test_database),
        ("Monitoreo", test_monitoring),
        ("Cron Jobs", test_cron_jobs),
        ("Integración", test_railway_integration)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"🔍 Ejecutando prueba: {test_name}")
        result = await test_func()
        results.append((test_name, result))
        print()

    # Resumen
    print("📊 Resumen de pruebas:")
    all_passed = True
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False

    print()
    if all_passed:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("🚂 Las características avanzadas de Railway están funcionando correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa la configuración.")

    # Información adicional
    print("\nℹ️  Información del entorno:")
    railway_info = railway.get_railway_info()
    for key, value in railway_info.items():
        if value:
            print(f"  {key}: {value}")

    return all_passed

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)