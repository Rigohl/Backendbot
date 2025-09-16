#!/usr/bin/env python3
"""
Sistema Completo de Automatización BackendBot
Ejecuta todo automáticamente: setup, servidor y verificaciones
"""

import os
import sys
import subprocess
import threading
import time
import signal
from pathlib import Path
import json

class CompleteAutoSystem:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.server_process = None
        self.verifier_process = None
        self.setup_complete = False

    def install_dependencies(self):
        """Instala dependencias automáticamente"""
        print("📦 Instalando dependencias...")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                print("[OK] Dependencias instaladas correctamente")
                return True
            else:
                print(f"[ERROR] Error instalando dependencias: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("[TIMEOUT] Timeout instalando dependencias")
            return False
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            return False

    def setup_database(self):
        """Configura la base de datos"""
        print("[DB] Configurando base de datos...")

        # Asegurar que existe el directorio data
        data_dir = self.project_root / "data"
        data_dir.mkdir(exist_ok=True)

        # Configurar .env si no existe
        env_file = self.project_root / ".env"
        if not env_file.exists():
            with open(env_file, 'w') as f:
                f.write('DATABASE_URL="sqlite:///data/backend_data.db"\n')
            print("[OK] Archivo .env creado")

        # Intentar PostgreSQL primero
        try:
            result = subprocess.run(
                [sys.executable, "setup_postgres.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("[OK] PostgreSQL configurado correctamente")
                return True
            else:
                print("[WARN] PostgreSQL no disponible, usando SQLite...")

        except subprocess.TimeoutExpired:
            print("[WARN] Timeout en PostgreSQL, usando SQLite...")
        except Exception as e:
            print(f"[WARN] Error con PostgreSQL: {e}, usando SQLite...")

        # Configurar SQLite como fallback
        sqlite_url = f'sqlite:///{data_dir / "backend_data.db"}'
        with open(env_file, 'w') as f:
            f.write(f'DATABASE_URL="{sqlite_url}"\n')

        print("[OK] SQLite configurado como fallback")
        return True

    def start_server_auto(self):
        """Inicia el servidor automáticamente"""
        print("[START] Iniciando servidor BackendBot...")

        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "start.py"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "PYTHONPATH": str(self.project_root / "src")}
            )

            # Esperar a que el servidor esté listo
            time.sleep(5)

            # Verificar que está corriendo
            if self.server_process.poll() is None:
                print("[OK] Servidor iniciado correctamente")
                print("[WEB] Servidor: http://localhost:8000")
                print("[STATS] Dashboard: http://localhost:8000/dashboard")
                print("[DOCS] API Docs: http://localhost:8000/docs")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                print(f"[ERROR] Error iniciando servidor: {stderr}")
                return False

        except Exception as e:
            print(f"[ERROR] Error: {e}")
            return False

    def run_verifications_auto(self):
        """Ejecuta verificaciones automáticamente"""
        print("[SEARCH] Ejecutando verificaciones automáticas...")

        try:
            self.verifier_process = subprocess.Popen(
                [sys.executable, "auto_verify.py"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Esperar a que terminen las verificaciones
            stdout, stderr = self.verifier_process.communicate(timeout=300)

            if self.verifier_process.returncode == 0:
                print("[OK] Verificaciones completadas")
                print("\n" + "="*50)
                print("[LIST] RESULTADOS:")
                print("="*50)
                print(stdout)
                return True
            else:
                print(f"[ERROR] Error en verificaciones: {stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("[TIMEOUT] Timeout en verificaciones")
            self.verifier_process.kill()
            return False
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            return False

    def run_complete_setup(self):
        """Ejecuta el setup completo automáticamente"""
        print("[BOT] BackendBot - Setup Completo Automático")
        print("=" * 50)

        # 1. Instalar dependencias
        if not self.install_dependencies():
            print("[ERROR] Falló instalación de dependencias")
            return False

        # 2. Configurar base de datos
        if not self.setup_database():
            print("[ERROR] Falló configuración de base de datos")
            return False

        # 3. Iniciar servidor
        if not self.start_server_auto():
            print("[ERROR] Falló inicio del servidor")
            return False

        # 4. Ejecutar verificaciones
        if not self.run_verifications_auto():
            print("[WARN] Verificaciones completadas con errores")

        self.setup_complete = True
        print("\n[SUCCESS] Setup completo finalizado!")
        print("[WEB] El servidor está corriendo en: http://localhost:8000")

        return True

    def monitor_and_maintain(self):
        """Monitorea el sistema y mantiene todo corriendo"""
        print("\n[STATS] Monitoreando sistema...")

        try:
            while self.setup_complete:
                # Verificar que el servidor sigue corriendo
                if self.server_process and self.server_process.poll() is not None:
                    print("[WARN] Servidor detenido, reiniciando...")
                    self.start_server_auto()

                time.sleep(30)  # Verificar cada 30 segundos

        except KeyboardInterrupt:
            print("\n[STOP] Deteniendo sistema...")
            self.stop_all()

    def stop_all(self):
        """Detiene todos los procesos"""
        print("[HALT] Deteniendo todos los procesos...")

        if self.server_process and self.server_process.poll() is None:
            print("Deteniendo servidor...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.server_process.kill()

        if self.verifier_process and self.verifier_process.poll() is None:
            print("Deteniendo verificaciones...")
            self.verifier_process.terminate()
            try:
                self.verifier_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.verifier_process.kill()

        print("[OK] Sistema detenido completamente")

def main():
    project_root = Path(__file__).parent
    system = CompleteAutoSystem(project_root)

    try:
        # Ejecutar setup completo
        if system.run_complete_setup():
            # Monitorear y mantener
            system.monitor_and_maintain()
        else:
            print("[ERROR] Setup falló")
            sys.exit(1)

    except KeyboardInterrupt:
        pass
    finally:
        system.stop_all()

if __name__ == "__main__":
    main()