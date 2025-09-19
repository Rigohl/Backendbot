#!/usr/bin/env python3
"""
BackendBot API Client - Acceso Directo con API Key
==================================================

Cliente para acceder a BackendBot API usando la API key maestra
del archivo .env para bypass de autenticación OAuth2.

Uso:
    python api_client.py --help

Ejemplos:
    # Ver estado del sistema
    python api_client.py status

    # Ejecutar bot organizer
    python api_client.py bot organizer scan --path /downloads

    # Crear backup
    python api_client.py backup create --name daily_backup

    # Enviar notificación
    python api_client.py notify send --message "Test message"
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BackendBotAPIClient:
    """Cliente para BackendBot API con acceso directo via API key"""

    def __init__(self, base_url: str = "https://127.0.0.1:48732", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Crear sesión HTTP con configuración optimizada"""
        session = requests.Session()

        # Configurar reintentos
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Headers por defecto
        session.headers.update({
            'User-Agent': 'BackendBot-API-Client/2.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

        # Agregar API key si está disponible
        if self.api_key:
            session.headers['X-API-Key'] = self.api_key

        return session

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realizar request HTTP con manejo de errores"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()

            if response.content:
                return response.json()
            return {"status": "success"}

        except requests.exceptions.SSLError:
            print("❌ Error SSL: Verifica que el servidor esté ejecutándose con HTTPS")
            sys.exit(1)
        except requests.exceptions.ConnectionError:
            print("❌ Error de conexión: Verifica que BackendBot esté ejecutándose")
            print(f"   URL: {url}")
            sys.exit(1)
        except requests.exceptions.Timeout:
            print("❌ Timeout: El servidor no responde")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            print(f"❌ Error HTTP {e.response.status_code}: {e.response.text}")
            sys.exit(1)
        except json.JSONDecodeError:
            print("❌ Error: Respuesta no válida del servidor")
            sys.exit(1)

    def health_check(self) -> Dict[str, Any]:
        """Verificar estado del servidor"""
        return self._make_request("GET", "/api/v1/health")

    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado general del sistema"""
        return self._make_request("GET", "/api/v1/dashboard/metrics")

    def get_bots_status(self) -> Dict[str, Any]:
        """Obtener estado de todos los bots"""
        return self._make_request("GET", "/api/v1/bots")

    def execute_bot(self, bot_name: str, action: str, **params) -> Dict[str, Any]:
        """Ejecutar acción en un bot específico"""
        data = {"action": action, **params}
        return self._make_request("POST", f"/api/v1/bots/{bot_name}/execute", json=data)

    def create_backup(self, name: str, strategy: str = "incremental") -> Dict[str, Any]:
        """Crear backup del sistema"""
        data = {"name": name, "strategy": strategy}
        return self._make_request("POST", "/api/v1/backup/create", json=data)

    def send_notification(self, message: str, priority: str = "info", channels: list = None) -> Dict[str, Any]:
        """Enviar notificación"""
        data = {
            "message": message,
            "priority": priority,
            "channels": channels or ["desktop"]
        }
        return self._make_request("POST", "/api/v1/notifications/send", json=data)

    def apply_power_profile(self, profile: str) -> Dict[str, Any]:
        """Aplicar perfil de energía"""
        data = {"profile": profile}
        return self._make_request("POST", "/api/v1/power/profile", json=data)


def load_api_key_from_env() -> Optional[str]:
    """Cargar API key desde archivo .env"""
    env_file = Path(".env")
    if not env_file.exists():
        return None

    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('BACKENDBOT_MASTER_API_KEY='):
                    return line.split('=', 1)[1].strip()
    except Exception:
        pass

    return None


def main():
    parser = argparse.ArgumentParser(
        description="BackendBot API Client - Acceso directo con API key",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('--url', default='https://127.0.0.1:48732',
                       help='URL base de BackendBot API')
    parser.add_argument('--api-key', help='API key (si no se especifica, se usa del .env)')

    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')

    # Comando status
    subparsers.add_parser('status', help='Mostrar estado general del sistema')

    # Comando health
    subparsers.add_parser('health', help='Verificar estado del servidor')

    # Comando bots
    bots_parser = subparsers.add_parser('bots', help='Mostrar estado de los bots')

    # Comando bot
    bot_parser = subparsers.add_parser('bot', help='Ejecutar acción en un bot')
    bot_parser.add_argument('bot_name', help='Nombre del bot')
    bot_parser.add_argument('action', help='Acción a ejecutar')
    bot_parser.add_argument('--path', help='Ruta para acciones de archivos')
    bot_parser.add_argument('--pattern', help='Patrón para búsquedas')

    # Comando backup
    backup_parser = subparsers.add_parser('backup', help='Operaciones de backup')
    backup_parser.add_argument('action', choices=['create'], help='Acción de backup')
    backup_parser.add_argument('--name', required=True, help='Nombre del backup')
    backup_parser.add_argument('--strategy', default='incremental',
                              choices=['full', 'incremental', 'differential'],
                              help='Estrategia de backup')

    # Comando notify
    notify_parser = subparsers.add_parser('notify', help='Enviar notificaciones')
    notify_parser.add_argument('action', choices=['send'], help='Acción de notificación')
    notify_parser.add_argument('--message', required=True, help='Mensaje de notificación')
    notify_parser.add_argument('--priority', default='info',
                              choices=['low', 'info', 'warning', 'error'],
                              help='Prioridad de notificación')
    notify_parser.add_argument('--channels', nargs='+', default=['desktop'],
                              help='Canales de notificación')

    # Comando power
    power_parser = subparsers.add_parser('power', help='Gestión de energía')
    power_parser.add_argument('action', choices=['profile'], help='Acción de energía')
    power_parser.add_argument('--profile', required=True,
                             choices=['high_performance', 'balanced', 'power_saver', 'ultra_low'],
                             help='Perfil de energía')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Cargar API key
    api_key = args.api_key or load_api_key_from_env()
    if not api_key:
        print("❌ Error: No se encontró API key")
        print("   Especifica --api-key o configura BACKENDBOT_MASTER_API_KEY en .env")
        sys.exit(1)

    # Crear cliente
    client = BackendBotAPIClient(args.url, api_key)

    try:
        if args.command == 'health':
            result = client.health_check()
            print("✅ Servidor funcionando correctamente")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'status':
            result = client.get_system_status()
            print("📊 Estado del Sistema BackendBot:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'bots':
            result = client.get_bots_status()
            print("🤖 Estado de los Bots:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'bot':
            params = {}
            if args.path:
                params['path'] = args.path
            if args.pattern:
                params['pattern'] = args.pattern

            result = client.execute_bot(args.bot_name, args.action, **params)
            print(f"🤖 Bot {args.bot_name} - Acción {args.action}:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'backup':
            if args.action == 'create':
                result = client.create_backup(args.name, args.strategy)
                print(f"💾 Backup '{args.name}' creado:")
                print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'notify':
            if args.action == 'send':
                result = client.send_notification(args.message, args.priority, args.channels)
                print("🔔 Notificación enviada:")
                print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'power':
            if args.action == 'profile':
                result = client.apply_power_profile(args.profile)
                print(f"⚡ Perfil de energía '{args.profile}' aplicado:")
                print(json.dumps(result, indent=2, ensure_ascii=False))

    except KeyboardInterrupt:
        print("\n⚠️  Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()