#!/usr/bin/env python3
"""
BackendBot - Script de Inicio Automático
========================================

Este script configura automáticamente BackendBot y lo inicia.

Uso:
    python start.py              # Inicia con configuración automática
    python start.py --help       # Muestra ayuda
    python start.py --setup-only # Solo configura, no inicia
    python start.py --db-only    # Solo configura base de datos
"""

import os
import sys
import subprocess
import time
import argparse
import webbrowser
from pathlib import Path

# Configuración del proyecto
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
BACKEND_DIR = SRC_DIR / "backendbot"

def check_python_version():
    """Verifica que Python sea compatible"""
    if sys.version_info < (3, 8):
        print("[ERROR] Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        sys.exit(1)
    print(f"[OK] Python {sys.version.split()[0]} detectado")

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'psycopg2', 'python-dotenv',
        'pydantic', 'psutil', 'jinja2'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("[ERROR] Faltan dependencias. Instalando...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("[OK] Dependencias instaladas")
        except subprocess.CalledProcessError:
            print("[ERROR] Error instalando dependencias")
            print("   Ejecuta: pip install -r requirements.txt")
            sys.exit(1)
    else:
        print("[OK] Dependencias verificadas")

def setup_database():
    """Configura la base de datos automáticamente"""
    print("\n[DB] Configurando base de datos...")

    # Verificar si PostgreSQL está disponible
    postgres_available = False
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='rigo007x10',
            host='localhost',
            port='5432',
            connect_timeout=5
        )
        conn.close()
        postgres_available = True
        print("[OK] PostgreSQL detectado y funcionando")
    except:
        print("[WARN]  PostgreSQL no disponible, usando SQLite")

    # Actualizar configuración
    env_file = PROJECT_ROOT / ".env"
    if postgres_available:
        db_url = "postgresql://user:rigo007x10@localhost:5432/backendbot_db"
        print("[NOTE] Configurado para PostgreSQL")
    else:
        db_url = f"sqlite:///{PROJECT_ROOT / 'data' / 'backend_data.db'}"
        print("[NOTE] Configurado para SQLite")

    # Crear directorio data si no existe
    data_dir = PROJECT_ROOT / "data"
    data_dir.mkdir(exist_ok=True)

    # Actualizar .env
    with open(env_file, 'w') as f:
        f.write(f'DATABASE_URL="{db_url}"\n')

    print(f"[OK] Base de datos configurada: {db_url}")

    # Si es PostgreSQL, ejecutar setup
    if postgres_available:
        print("[CONFIG] Ejecutando configuración de PostgreSQL...")
        try:
            subprocess.run([
                sys.executable, "setup_postgres.py"
            ], check=True, capture_output=True)
            print("[OK] PostgreSQL configurado correctamente")
        except subprocess.CalledProcessError as e:
            print(f"[WARN]  Error en configuración PostgreSQL: {e}")
            print("   Continuando con SQLite...")

            # Cambiar a SQLite
            db_url = f"sqlite:///{PROJECT_ROOT / 'data' / 'backend_data.db'}"
            with open(env_file, 'w') as f:
                f.write(f'DATABASE_URL="{db_url}"\n')
            print("[NOTE] Cambiado a SQLite")

def start_server():
    """Inicia el servidor FastAPI"""
    print("\n[START] Iniciando BackendBot...")

    # Asegurar que estamos en el directorio correcto
    os.chdir(PROJECT_ROOT)

    # Agregar src al path
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

    try:
        # Iniciar servidor con uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn",
            "backendbot.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ]

        # Configurar PYTHONPATH
        env = os.environ.copy()
        env['PYTHONPATH'] = str(SRC_DIR) + os.pathsep + env.get('PYTHONPATH', '')

        print("[WEB] Servidor iniciándose en: http://localhost:8000")
        print("[STATS] Dashboard disponible en: http://localhost:8000/dashboard")
        print("[DOCS] Documentación API en: http://localhost:8000/docs")
        print("")
        print("[STOP]  Presiona Ctrl+C para detener el servidor")
        print("=" * 50)

        # Abrir navegador después de 3 segundos
        def open_browser():
            time.sleep(3)
            try:
                webbrowser.open("http://localhost:8000/dashboard")
            except:
                pass  # Ignorar errores del navegador

        # Iniciar hilo para abrir navegador
        import threading
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        # Ejecutar servidor
        subprocess.run(cmd, env=env)

    except KeyboardInterrupt:
        print("\n[STOP]  Servidor detenido por el usuario")
    except Exception as e:
        print(f"[ERROR] Error iniciando servidor: {e}")
        sys.exit(1)

def show_info():
    """Muestra información del proyecto"""
    print("[BOT] BackendBot - La Colmena")
    print("=" * 40)
    print("🏗️  Arquitectura: Microservicios (Bots)")
    print("[WEB] Framework: FastAPI + SQLAlchemy")
    print("[DB]  Base de datos: PostgreSQL/SQLite")
    print("[STATS] Puerto: 8000")
    print("")
    print("📁 Estructura del proyecto:")
    print("   ├── src/backendbot/          # Código principal")
    print("   ├── src/backendbot/bots/     # Bots trabajadores")
    print("   ├── data/                    # Datos y base de datos")
    print("   ├── logs/                    # Archivos de log")
    print("   └── tests/                   # Pruebas")
    print("")
    print("[START] Funcionalidades:")
    print("   • Monitoreo de sistema en tiempo real")
    print("   • Gestión inteligente de archivos")
    print("   • Indexación y búsqueda de archivos")
    print("   • Dashboard web")
    print("   • API REST completa")

def main():
    parser = argparse.ArgumentParser(description="BackendBot - Script de Inicio")
    parser.add_argument('--setup-only', action='store_true',
                       help='Solo configurar, no iniciar servidor')
    parser.add_argument('--db-only', action='store_true',
                       help='Solo configurar base de datos')
    parser.add_argument('--info', action='store_true',
                       help='Mostrar información del proyecto')

    args = parser.parse_args()

    print("[BOT] BackendBot - Inicio Automático")
    print("=" * 40)

    if args.info:
        show_info()
        return

    # Verificaciones iniciales
    check_python_version()
    check_dependencies()

    # Configurar base de datos
    if not args.setup_only:
        setup_database()

    if args.db_only:
        print("[OK] Configuración de base de datos completada")
        return

    if args.setup_only:
        print("[OK] Configuración completada")
        return

    # Iniciar servidor
    start_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nHasta luego!")
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)