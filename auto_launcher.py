#!/usr/bin/env python3
"""
Launcher Automático BackendBot
Inicia servidor y verificaciones en paralelo
"""

import os
import sys
import subprocess
import threading
import time
import signal
from pathlib import Path

class AutoLauncher:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.server_process = None
        self.verifier_process = None

    def start_server_background(self):
        """Inicia el servidor en segundo plano"""
        print("[START] Iniciando servidor BackendBot en segundo plano...")

        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "start.py"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("[OK] Servidor iniciado (PID: {})".format(self.server_process.pid))

            # Esperar a que el servidor esté listo
            time.sleep(3)
            return True
        except Exception as e:
            print(f"[ERROR] Error iniciando servidor: {e}")
            return False

    def start_verifications_background(self):
        """Inicia verificaciones en segundo plano"""
        print("[SEARCH] Iniciando verificaciones automáticas...")

        try:
            self.verifier_process = subprocess.Popen(
                [sys.executable, "auto_verify.py"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("[OK] Verificaciones iniciadas (PID: {})".format(self.verifier_process.pid))
            return True
        except Exception as e:
            print(f"[ERROR] Error iniciando verificaciones: {e}")
            return False

    def monitor_processes(self):
        """Monitorea los procesos en ejecución"""
        print("\n[STATS] Monitoreando procesos...")

        try:
            while True:
                if self.server_process and self.server_process.poll() is not None:
                    print("[WARN] Servidor detenido")
                    break

                if self.verifier_process and self.verifier_process.poll() is not None:
                    print("[OK] Verificaciones completadas")
                    # Leer resultados
                    if self.verifier_process.stdout:
                        output = self.verifier_process.stdout.read()
                        if output:
                            print("\n[LIST] Resultados de verificación:")
                            print(output)
                    break

                time.sleep(2)

        except KeyboardInterrupt:
            print("\n[STOP] Deteniendo procesos...")
            self.stop_all()

    def stop_all(self):
        """Detiene todos los procesos"""
        if self.server_process and self.server_process.poll() is None:
            print("[HALT] Deteniendo servidor...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()

        if self.verifier_process and self.verifier_process.poll() is None:
            print("[HALT] Deteniendo verificaciones...")
            self.verifier_process.terminate()
            try:
                self.verifier_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.verifier_process.kill()

        print("[OK] Todos los procesos detenidos")

    def run(self):
        """Ejecuta el launcher automático"""
        print("[BOT] BackendBot Auto-Launcher")
        print("=" * 40)

        # Iniciar servidor
        if not self.start_server_background():
            print("[ERROR] No se pudo iniciar el servidor")
            return

        # Iniciar verificaciones
        if not self.start_verifications_background():
            print("[ERROR] No se pudieron iniciar las verificaciones")
            self.stop_all()
            return

        # Monitorear
        try:
            self.monitor_processes()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all()

def main():
    project_root = Path(__file__).parent
    launcher = AutoLauncher(project_root)
    launcher.run()

if __name__ == "__main__":
    main()