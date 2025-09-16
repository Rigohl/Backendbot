#!/usr/bin/env python3
"""
Sistema de Verificación Automática BackendBot
Ejecuta verificaciones en paralelo usando múltiples terminales
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

class AutoVerifier:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.results = {}
        self.active_terminals = []

    def run_command_async(self, command, name, cwd=None):
        """Ejecuta un comando en segundo plano"""
        def execute():
            try:
                print(f"[START] Iniciando verificación: {name}")
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=cwd or self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutos timeout
                )
                self.results[name] = {
                    'status': 'success' if result.returncode == 0 else 'error',
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                print(f"[OK] {'Completado' if result.returncode == 0 else 'Error en'}: {name}")
            except subprocess.TimeoutExpired:
                self.results[name] = {'status': 'timeout', 'error': 'Timeout after 5 minutes'}
                print(f"[TIMEOUT] Timeout en: {name}")
            except Exception as e:
                self.results[name] = {'status': 'error', 'error': str(e)}
                print(f"[ERROR] Error en: {name} - {e}")

        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        self.active_terminals.append((name, thread))
        return thread

    def verify_python_syntax(self):
        """Verifica sintaxis de todos los archivos Python"""
        python_files = list(self.project_root.rglob("*.py"))
        commands = []

        for py_file in python_files:
            rel_path = py_file.relative_to(self.project_root)
            commands.append(f'python -m py_compile "{rel_path}"')

        return commands

    def verify_imports(self):
        """Verifica imports de módulos"""
        return [
            'python -c "import sys; sys.path.insert(0, \'src\'); import backendbot.main"',
            'python -c "import sys; sys.path.insert(0, \'src\'); import backendbot.models"',
            'python -c "import sys; sys.path.insert(0, \'src\'); import backendbot.config"',
            'python -c "import sys; sys.path.insert(0, \'src\'); from backendbot.bots import bot_guardian, bot_monitor, bot_organizer, bot_indexer"'
        ]

    def verify_database(self):
        """Verifica configuración de base de datos"""
        return [
            'python -c "try: from src.backendbot.utils.db import get_db; db = next(get_db()); print(\\"DB connection OK\\"); except Exception as e: print(f\\"DB Error: {e}\\")"',
            'python -c "try: from src.backendbot.models import SystemEvent, BotAction; print(\\"Models OK\\"); except Exception as e: print(f\\"Models Error: {e}\\")"'
        ]

    def verify_dependencies(self):
        """Verifica dependencias"""
        return [
            'python -c "import fastapi, uvicorn, sqlalchemy, psycopg2, pydantic; print(\'Core deps OK\')"',
            'python -c "import psutil, aiofiles, httpx; print(\'Extra deps OK\')"'
        ]

    def verify_file_structure(self):
        """Verifica estructura de archivos"""
        required_files = [
            'src/backendbot/main.py',
            'src/backendbot/models.py',
            'src/backendbot/config.py',
            'requirements.txt',
            '.env'
        ]

        commands = []
        for file_path in required_files:
            # Escapar comillas correctamente para el comando
            escaped_path = file_path.replace('"', '\\"')
            commands.append(f'python -c "import os; print(\\"{escaped_path}: \\" + (\\"OK\\" if os.path.exists(\\"{escaped_path}\\") else \\"MISSING\\"))"')

        return commands

    def verify_config_files(self):
        """Verifica archivos de configuración"""
        return [
            'python -c "import os; print(\\".env exists: \\" + str(os.path.exists(\\".env\\")))"',
            'python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(\\"DATABASE_URL: \\" + str(os.getenv(\\"DATABASE_URL\\", \\"NOT_SET\\")))"'
        ]

    def verify_api_endpoints(self):
        """Verifica endpoints de la API"""
        return [
            'python -c "import requests; r = requests.get(\'http://localhost:8000/docs\'); print(f\'API docs: {r.status_code}\')"',
            'python -c "import requests; r = requests.get(\'http://localhost:8000/dashboard\'); print(f\'Dashboard: {r.status_code}\')"'
        ]

    def run_all_verifications(self):
        """Ejecuta todas las verificaciones en paralelo"""
        print("[BOT] Iniciando verificación automática del BackendBot...")
        print("=" * 60)

        # Preparar todos los comandos
        all_commands = []

        # Estructura de archivos
        file_commands = self.verify_file_structure()
        for i, cmd in enumerate(file_commands):
            all_commands.append((cmd, f"file_structure_{i}", self.project_root))

        # Configuración
        config_commands = self.verify_config_files()
        for i, cmd in enumerate(config_commands):
            all_commands.append((cmd, f"config_{i}", self.project_root))

        # Sintaxis Python
        syntax_commands = self.verify_python_syntax()
        for i, cmd in enumerate(syntax_commands):
            all_commands.append((cmd, f"syntax_py_{i}", self.project_root))

        # Imports
        import_commands = self.verify_imports()
        for i, cmd in enumerate(import_commands):
            all_commands.append((cmd, f"import_{i}", self.project_root))

        # Base de datos
        db_commands = self.verify_database()
        for i, cmd in enumerate(db_commands):
            all_commands.append((cmd, f"database_{i}", self.project_root))

        # Dependencias
        dep_commands = self.verify_dependencies()
        for i, cmd in enumerate(dep_commands):
            all_commands.append((cmd, f"dependencies_{i}", self.project_root))

        # API (requiere servidor corriendo)
        api_commands = self.verify_api_endpoints()
        for i, cmd in enumerate(api_commands):
            all_commands.append((cmd, f"api_{i}", self.project_root))

        # Ejecutar en paralelo con ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            for command, name, cwd in all_commands:
                future = executor.submit(self.run_command_async, command, name, cwd)
                futures.append(future)

            # Esperar a que terminen
            for future in as_completed(futures):
                pass

        # Esperar a que todos los hilos terminen
        for name, thread in self.active_terminals:
            thread.join(timeout=1)

        return self.results

    def generate_report(self):
        """Genera un reporte de resultados"""
        print("\n[STATS] REPORTE DE VERIFICACIÓN")
        print("=" * 60)

        success_count = 0
        error_count = 0
        timeout_count = 0

        for name, result in self.results.items():
            status = result.get('status', 'unknown')
            if status == 'success':
                success_count += 1
                print(f"[OK] {name}")
            elif status == 'timeout':
                timeout_count += 1
                print(f"[TIMEOUT] {name} - TIMEOUT")
            else:
                error_count += 1
                print(f"[ERROR] {name}")
                if 'stderr' in result and result['stderr']:
                    print(f"   Error: {result['stderr'][:100]}...")

        print(f"\n[REPORT] Resumen:")
        print(f"[OK] Exitosos: {success_count}")
        print(f"[ERROR] Errores: {error_count}")
        print(f"[TIMEOUT] Timeouts: {timeout_count}")

        return {
            'total': len(self.results),
            'success': success_count,
            'errors': error_count,
            'timeouts': timeout_count
        }

def main():
    project_root = Path(__file__).parent
    verifier = AutoVerifier(project_root)

    # Ejecutar verificaciones
    results = verifier.run_all_verifications()

    # Generar reporte
    summary = verifier.generate_report()

    # Guardar resultados detallados
    with open('verification_results.json', 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'summary': summary,
            'details': results
        }, f, indent=2)

    print("\n[SAVE] Resultados guardados en: verification_results.json")
    print("[SUCCESS] Verificación automática completada!")

if __name__ == "__main__":
    main()