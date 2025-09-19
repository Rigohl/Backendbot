/* Entire file content removed */
#!/usr/bin/env python3
"""
BackendBot API Server - Modo Seguro Local
===============    # Configurar HTTPS si se solicita
    ssl_config = None
    if args.https:
        cert_path = Path(args.ssl_cert)
        key_path = Path(args.ssl_key)

        if not cert_path.exists() or not key_path.exists():
            print("❌ Error: Certificados SSL no encontrados")
            print(f"   Certificado: {cert_path}")
            print(f"   Clave: {key_path}")
            print("   Ejecuta: python generate_ssl_cert.py")
            sys.exit(1)

        ssl_config = {
            "certfile": str(cert_path),
            "keyfile": str(key_path)
        }
        protocol = "https"
    else:
        protocol = "http"

    if not args.visible:
        print("� BackendBot API Server - Modo Seguro Activado")
        print("🌐 Solo accesible desde localhost (127.0.0.1)")
        print(f"� Puerto seguro: {args.port}")
        print(f"🔒 HTTPS: {'Habilitado' if args.https else 'Deshabilitado'}")
        print("� Modo invisible: Sin output visible")
        print(f"📖 Documentación: {protocol}://127.0.0.1:{args.port}/docs")
        print(f"� Health Check: {protocol}://127.0.0.1:{args.port}/api/v1/health")
        print("🛡️  Servidor ejecutándose en segundo plano...")
        print()==================

Servidor de API principal para BackendBot.
Ejecuta la aplicación FastAPI en modo seguro local.

Configuración de seguridad:
- Solo localhost (127.0.0.1)
- Puerto no estándar (48732)
- Sin acceso externo
- Ejecución en segundo plano invisible

Uso:
    python api_server.py

Opciones avanzadas:
    --port PORT          Puerto personalizado (default: 48732)
    --visible            Mostrar output (desactiva modo invisible)

Autor: BackendBot Team
Versión: 0.1.0
"""

import argparse
import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path para importar backendbot
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

try:
    import uvicorn
    from backendbot.apps.api.main import app
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Asegúrate de tener instaladas todas las dependencias:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def main():
    """Función principal para ejecutar el servidor API."""
    parser = argparse.ArgumentParser(description="BackendBot API Server - Modo Seguro")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host (SIEMPRE debe ser 127.0.0.1 para seguridad)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=48732,
        help="Puerto seguro no estándar (default: 48732)"
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Mostrar output del servidor (desactiva modo invisible)"
    )
    parser.add_argument(
        "--ssl-cert",
        default="certs/backendbot_cert.pem",
        help="Ruta al certificado SSL (default: certs/backendbot_cert.pem)"
    )
    parser.add_argument(
        "--ssl-key",
        default="certs/backendbot_key.pem",
        help="Ruta a la clave privada SSL (default: certs/backendbot_key.pem)"
    )
    parser.add_argument(
        "--https",
        action="store_true",
        help="Habilitar HTTPS con certificado SSL"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Número de workers (default: 1)"
    )
    parser.add_argument(
        "--log-level",
        default="warning",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Nivel de logging (default: warning para modo invisible)"
    )

    args = parser.parse_args()

    # Validación de seguridad
    if args.host != "127.0.0.1":
        print("⚠️  ADVERTENCIA: Por seguridad, el host debe ser 127.0.0.1")
        print("� Cambiando automáticamente a 127.0.0.1")
        args.host = "127.0.0.1"

    if not args.visible:
        print("� BackendBot API Server - Modo Seguro Activado")
        print("🌐 Solo accesible desde localhost (127.0.0.1)")
        print(f"� Puerto seguro: {args.port}")
        print("� Modo invisible: Sin output visible")
        print("📖 Documentación: http://127.0.0.1:48732/docs")
        print("� Health Check: http://127.0.0.1:48732/api/v1/health")
        print("🛡️  Servidor ejecutándose en segundo plano...")
        print()

        # Redirigir output a null para modo invisible
        if os.name == 'nt':  # Windows
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
        else:  # Unix/Linux
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
            os.dup2(devnull, sys.stderr.fileno())

    # Configurar HTTPS si se solicita
    ssl_config = None
    protocol = "http"
    if args.https:
        cert_path = Path(args.ssl_cert)
        key_path = Path(args.ssl_key)

        if not cert_path.exists() or not key_path.exists():
            if args.visible:
                print("❌ Error: Certificados SSL no encontrados")
                print(f"   Certificado: {cert_path}")
                print(f"   Clave: {key_path}")
                print("   Ejecuta: python generate_ssl_cert.py")
            sys.exit(1)

        ssl_config = {
            "certfile": str(cert_path),
            "keyfile": str(key_path)
        }
        protocol = "https"

    if not args.visible:
        print("� BackendBot API Server - Modo Seguro Activado")
        print("🌐 Solo accesible desde localhost (127.0.0.1)")
        print(f"� Puerto seguro: {args.port}")
        print(f"🔒 HTTPS: {'Habilitado' if args.https else 'Deshabilitado'}")
        print("� Modo invisible: Sin output visible")
        print(f"📖 Documentación: {protocol}://127.0.0.1:{args.port}/docs")
        print(f"� Health Check: {protocol}://127.0.0.1:{args.port}/api/v1/health")
        print("🛡️  Servidor ejecutándose en segundo plano...")
        print()

    try:
        uvicorn.run(
            "backendbot.apps.api.main:app",
            host=args.host,
            port=args.port,
            reload=False,  # Desactivado para producción
            workers=args.workers,
            log_level=args.log_level,
            access_log=False if not args.visible else True,  # Sin logs de acceso en modo invisible
            ssl_certfile=ssl_config["certfile"] if ssl_config else None,
            ssl_keyfile=ssl_config["keyfile"] if ssl_config else None,
        )
    except KeyboardInterrupt:
        if args.visible:
            print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        if args.visible:
            print(f"❌ Error al iniciar el servidor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()