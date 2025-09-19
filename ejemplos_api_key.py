#!/usr/bin/env python3
"""
BackendBot - Ejemplos de Uso con API Key
=========================================

Ejemplos prácticos de cómo usar BackendBot API con acceso directo
usando la API key del archivo .env.

Estos ejemplos muestran cómo:
- Verificar estado del sistema
- Controlar bots
- Gestionar backups
- Enviar notificaciones
- Cambiar perfiles de energía

Uso:
    python ejemplos_api_key.py

Requisitos:
- BackendBot API ejecutándose
- API key configurada en .env
"""

import json
import sys
from pathlib import Path

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from api_client import BackendBotAPIClient, load_api_key_from_env


def print_separator(title: str):
    """Imprimir separador con título"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def ejemplo_health_check(client: BackendBotAPIClient):
    """Ejemplo: Health check"""
    print_separator("1. HEALTH CHECK")
    try:
        result = client.health_check()
        print("✅ Servidor funcionando:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")


def ejemplo_estado_sistema(client: BackendBotAPIClient):
    """Ejemplo: Estado del sistema"""
    print_separator("2. ESTADO DEL SISTEMA")
    try:
        result = client.get_system_status()
        print("📊 Estado del sistema:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")


def ejemplo_estado_bots(client: BackendBotAPIClient):
    """Ejemplo: Estado de los bots"""
    print_separator("3. ESTADO DE LOS BOTS")
    try:
        result = client.get_bots_status()
        print("🤖 Estado de los bots:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")


def ejemplo_ejecutar_bot(client: BackendBotAPIClient):
    """Ejemplo: Ejecutar bot organizer"""
    print_separator("4. EJECUTAR BOT ORGANIZER")
    try:
        result = client.execute_bot("organizer", "scan", path=str(Path.home() / "Downloads"))
        print("🤖 Bot organizer ejecutado:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")


def ejemplo_crear_backup(client: BackendBotAPIClient):
    """Ejemplo: Crear backup"""
    print_separator("5. CREAR BACKUP")
    try:
        result = client.create_backup("demo_backup", "incremental")
        print("💾 Backup creado:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")


def ejemplo_enviar_notificacion(client: BackendBotAPIClient):
    """Ejemplo: Enviar notificación"""
    print_separator("6. ENVIAR NOTIFICACIÓN")
    try:
        result = client.send_notification(
            message="Demo: Notificación desde API Key",
            priority="info",
            channels=["desktop"]
        )
        print("🔔 Notificación enviada:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")


def ejemplo_cambiar_perfil_energia(client: BackendBotAPIClient):
    """Ejemplo: Cambiar perfil de energía"""
    print_separator("7. CAMBIAR PERFIL DE ENERGÍA")
    try:
        result = client.apply_power_profile("balanced")
        print("⚡ Perfil de energía aplicado:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")


def ejemplo_buscar_archivos(client: BackendBotAPIClient):
    """Ejemplo: Buscar archivos con indexer"""
    print_separator("8. BUSCAR ARCHIVOS")
    try:
        result = client.execute_bot("indexer", "search", pattern="*.txt")
        print("🔍 Búsqueda de archivos:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")


def ejemplo_auditor_archivos(client: BackendBotAPIClient):
    """Ejemplo: Auditor de archivos antiguos"""
    print_separator("9. AUDITOR DE ARCHIVOS ANTIGUOS")
    try:
        result = client.execute_bot("auditor_files", "scan")
        print("📂 Análisis de archivos antiguos:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")


def ejemplo_auditor_programas(client: BackendBotAPIClient):
    """Ejemplo: Auditor de programas no usados"""
    print_separator("10. AUDITOR DE PROGRAMAS")
    try:
        result = client.execute_bot("auditor_programs", "scan")
        print("💻 Análisis de programas no usados:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Función principal con todos los ejemplos"""
    print("🐝 BackendBot - Ejemplos de Uso con API Key")
    print("=" * 60)

    # Cargar API key
    api_key = load_api_key_from_env()
    if not api_key:
        print("❌ Error: No se encontró API key en .env")
        print("   Configura BACKENDBOT_MASTER_API_KEY en tu archivo .env")
        sys.exit(1)

    print(f"✅ API Key encontrada: {api_key[:10]}...")
    print("🌐 Conectando a BackendBot API...")

    # Crear cliente
    client = BackendBotAPIClient(api_key=api_key)

    # Ejecutar ejemplos
    try:
        ejemplo_health_check(client)
        ejemplo_estado_sistema(client)
        ejemplo_estado_bots(client)
        ejemplo_ejecutar_bot(client)
        ejemplo_crear_backup(client)
        ejemplo_enviar_notificacion(client)
        ejemplo_cambiar_perfil_energia(client)
        ejemplo_buscar_archivos(client)
        ejemplo_auditor_archivos(client)
        ejemplo_auditor_programas(client)

        print_separator("✅ TODOS LOS EJEMPLOS COMPLETADOS")
        print("🎉 ¡BackendBot API con API Key funciona correctamente!")
        print("\n💡 Consejos:")
        print("   - Usa 'python api_client.py --help' para ver comandos disponibles")
        print("   - Modifica los ejemplos según tus necesidades")
        print("   - La API key permite acceso directo sin OAuth2")

    except KeyboardInterrupt:
        print("\n⚠️  Ejemplos interrumpidos por el usuario")
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        print("💡 Asegúrate de que BackendBot esté ejecutándose:")
        print("   python api_server.py --https")


if __name__ == "__main__":
    main()