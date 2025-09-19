"""
Demo Organizer Worker
=====================

Demostración completa del OrganizerWorker mostrando:
- Organización de archivos por tipo
- Movimiento de archivos
- Eliminación de archivos temporales
- Sistema de backups
- Callbacks de organización
- Estadísticas y historial

Autor: BackendBot Team
Versión: 0.1.0
"""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from backendbot.packages.bots.base_bot import BotState
from backendbot.packages.bots.organizer_worker import OrganizerWorker


def create_test_files(base_dir: Path):
    """Crear archivos de prueba para la demostración."""
    print(f"📁 Creando archivos de prueba en: {base_dir}")

    # Crear archivos de diferentes tipos
    files_to_create = [
        ("document.pdf", "Contenido de un documento PDF"),
        ("presentation.pptx", "Contenido de una presentación PowerPoint"),
        ("spreadsheet.xlsx", "Datos de una hoja de cálculo"),
        ("photo.jpg", "Datos binarios de imagen JPEG"),
        ("diagram.png", "Datos binarios de diagrama PNG"),
        ("music.mp3", "Datos binarios de archivo MP3"),
        ("video.mp4", "Datos binarios de video MP4"),
        ("script.py", "print('Hola mundo')"),
        ("config.json", '{"setting": "value"}'),
        ("readme.md", "# Documentación"),
        ("temp.tmp", "Archivo temporal"),
        ("~backup.txt", "Archivo de backup temporal"),
        ("cache.dat", "Datos de caché"),
        ("log.txt", "Archivo de log de aplicación"),
    ]

    # Crear archivos grandes (más de 1MB) para pasar filtros
    large_content = "x" * (1024 * 1024 + 100)  # 1MB + 100 bytes

    for filename, content in files_to_create:
        file_path = base_dir / filename
        if filename.endswith((".jpg", ".png", ".mp3", ".mp4")):
            # Archivos binarios simulados
            file_path.write_bytes(large_content.encode("utf-8") + b"\x00\x01\x02")
        else:
            file_path.write_text(large_content + content)

    # Crear algunos archivos en subdirectorios
    sub_dir = base_dir / "project_files"
    sub_dir.mkdir()

    (sub_dir / "main.py").write_text(large_content + "def main(): pass")
    (sub_dir / "utils.py").write_text(large_content + "def helper(): pass")
    (sub_dir / "data.csv").write_text(large_content + "name,value\nitem1,100")

    print(f"✅ Creados {len(files_to_create) + 3} archivos de prueba")

def organization_callback(result):
    """Callback para mostrar resultados de organización."""
    print("\n📊 CALLBACK DE ORGANIZACIÓN:")
    print(f"   Procesados: {result.files_processed}")
    print(f"   Movidos: {result.files_moved}")
    print(f"   Eliminados: {result.files_deleted}")
    print(f"   Errores: {result.errors_count}")
    print(f"   Duración: {result.duration_seconds:.2f}s")
    if result.errors:
        print(f"   ⚠️  Errores encontrados: {len(result.errors)}")

def demo_dry_run():
    """Demostración en modo simulación (dry run)."""
    print("\n" + "=" * 60)
    print("🎭 DEMO 1: ORGANIZER WORKER - MODO SIMULACIÓN (DRY RUN)")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Crear archivos de prueba
        create_test_files(temp_path)

        # Configurar Organizer Worker
        config = {
            "scan_paths": [str(temp_path)],
            "dry_run": True,  # Modo simulación
            "organization_rules": {
                "by_type": True,
                "min_file_size_mb": 1,  # Solo archivos > 1MB
                "max_file_age_days": 365,  # Todos los archivos
                "auto_delete_temp": True,
            },
            "file_categories": {
                "documents": [".pdf", ".docx", ".txt", ".md"],
                "spreadsheets": [".xlsx", ".csv"],
                "images": [".jpg", ".png", ".gif"],
                "audio": [".mp3", ".wav"],
                "video": [".mp4", ".avi"],
                "code": [".py", ".js", ".html", ".css"],
                "temp": [".tmp", ".bak", ".cache"],
                "logs": [".log"],
            },
        }

        # Crear y configurar worker
        worker = OrganizerWorker(bot_id="demo-organizer", name="Demo Organizer")
        worker.config.update(config)

        # Agregar callback
        worker.add_organization_callback(organization_callback)

        print(f"\n🤖 Worker configurado: {worker}")
        print(f"📂 Directorios a escanear: {worker.scan_paths}")
        print(f"📋 Reglas: {worker.organization_rules}")

        # Ejecutar organización
        print("\n🚀 Ejecutando organización...")
        start_time = datetime.now()

        result = worker.execute_task()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"⏱️  Duración: {duration:.2f}s")
        print(f"✅ Éxito: {result['success']}")

        if result["success"]:
            stats = result["result"]
            print("\n📈 RESULTADOS:")
            print(f"   📁 Archivos procesados: {stats['files_processed']}")
            print(f"   📦 Archivos movidos: {stats['files_moved']}")
            print(f"   🗑️  Archivos eliminados: {stats['files_deleted']}")
            print(f"   ⚠️  Errores: {stats['errors_count']}")

            # Mostrar estructura final
            print("\n📂 ESTRUCTURA FINAL (SIMULADA):")
            show_directory_structure(temp_path)

        # Mostrar estadísticas
        print("\n📊 ESTADÍSTICAS DEL WORKER:")
        worker_stats = worker.get_statistics()
        for key, value in worker_stats.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")

        # Mostrar historial
        print("\n📚 HISTORIAL DE ORGANIZACIÓN:")
        history = worker.get_organization_history()
        for i, entry in enumerate(history[-3:], 1):  # Últimas 3 entradas
            print(
                f"   {i}. {entry['files_processed']} archivos, {entry['files_moved']} movidos"
            )

def demo_real_execution():
    """Demostración con ejecución real."""
    print("\n" + "=" * 60)
    print("🔥 DEMO 2: ORGANIZER WORKER - EJECUCIÓN REAL")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Crear archivos de prueba
        create_test_files(temp_path)

        # Configurar Organizer Worker para ejecución real
        config = {
            "scan_paths": [str(temp_path)],
            "dry_run": False,  # Ejecución real
            "organization_rules": {
                "by_type": True,
                "min_file_size_mb": 1,
                "max_file_age_days": 365,
                "auto_delete_temp": True,
            },
            "file_categories": {
                "documents": [".pdf", ".docx", ".txt", ".md"],
                "spreadsheets": [".xlsx", ".csv"],
                "images": [".jpg", ".png", ".gif"],
                "audio": [".mp3", ".wav"],
                "video": [".mp4", ".avi"],
                "code": [".py", ".js", ".html", ".css"],
                "temp": [".tmp", ".bak", ".cache"],
                "logs": [".log"],
            },
            "backup_dir": str(temp_path / "backups"),
        }

        # Crear y configurar worker
        worker = OrganizerWorker(
            bot_id="demo-organizer-real", name="Demo Organizer Real"
        )
        worker.config.update(config)

        # Agregar callback
        worker.add_organization_callback(organization_callback)

        print(f"\n🤖 Worker configurado: {worker}")
        print(f"📂 Directorios a escanear: {worker.scan_paths}")
        print(f"🔥 Modo: EJECUCIÓN REAL (archivos serán movidos/eliminados)")

        # Mostrar estructura inicial
        print("\n📂 ESTRUCTURA INICIAL:")
        show_directory_structure(temp_path)

        # Ejecutar organización
        print("\n🚀 Ejecutando organización REAL...")
        start_time = datetime.now()

        result = worker.execute_task()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"⏱️  Duración: {duration:.2f}s")
        print(f"✅ Éxito: {result['success']}")

        if result["success"]:
            stats = result["result"]
            print("\n📈 RESULTADOS:")
            print(f"   📁 Archivos procesados: {stats['files_processed']}")
            print(f"   📦 Archivos movidos: {stats['files_moved']}")
            print(f"   🗑️  Archivos eliminados: {stats['files_deleted']}")
            print(f"   ⚠️  Errores: {stats['errors_count']}")

            # Mostrar estructura final
            print("\n📂 ESTRUCTURA FINAL:")
            show_directory_structure(temp_path)

            # Verificar backups
            backup_dir = temp_path / "backups"
            if backup_dir.exists():
                backups = list(backup_dir.glob("*.bak"))
                print(f"\n💾 BACKUPS CREADOS: {len(backups)} archivos")
                for backup in backups[:3]:  # Mostrar primeros 3
                    print(f"   📄 {backup.name}")


def demo_threading():
    """Demostración de funcionamiento con threading."""
    print("\n" + "=" * 60)
    print("🧵 DEMO 3: ORGANIZER WORKER - THREADING")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Crear archivos de prueba
        create_test_files(temp_path)

        # Configurar worker con intervalo corto para demo
        config = {
            "scan_paths": [str(temp_path)],
            "dry_run": True,
            "organization_rules": {
                "by_type": True,
                "min_file_size_mb": 1,
                "max_file_age_days": 365,
                "auto_delete_temp": True,
            },
            "file_categories": {
                "documents": [".pdf", ".docx", ".txt", ".md"],
                "code": [".py", ".js"],
                "temp": [".tmp"],
            },
        }

        worker = OrganizerWorker(bot_id="demo-threading", name="Demo Threading")
        worker.config.update(config)

        print(f"🤖 Iniciando worker con threading: {worker}")
        print(f"⏰ Intervalo de ejecución: {worker.get_execution_interval()} segundos")

        # Iniciar worker
        worker.start()
        print(f"✅ Worker iniciado. Estado: {worker.state}")

        # Ejecutar tarea manualmente para demo
        print("\n🚀 Ejecutando tarea manualmente...")
        result = worker.execute_task()

        if result["success"]:
            stats = result["result"]
            print(
                f"✅ Organización completada: {stats['files_processed']} archivos procesados"
            )

        # Mostrar estado
        print(f"📊 Estado actual: {worker.state}")
        print(f"📈 Estadísticas: {worker.get_statistics()}")

        # Detener worker
        print("\n🛑 Deteniendo worker...")
        worker.stop()
        print(f"✅ Worker detenido. Estado final: {worker.state}")


def show_directory_structure(base_path: Path, indent: str = ""):
    """Mostrar estructura de directorios de forma recursiva."""
    try:
        for item in sorted(base_path.iterdir()):
            if item.is_file():
                size_mb = item.stat().st_size / (1024 * 1024)
                print(f"{indent}📄 {item.name} ({size_mb:.2f} MB)")
            elif item.is_dir() and not item.name.startswith("."):
                print(f"{indent}📁 {item.name}/")
                show_directory_structure(item, indent + "   ")
    except PermissionError:
        print(f"{indent}🔒 [Sin permisos]")


def main():
    """Función principal de la demo."""
    print("🎯 DEMO COMPLETA - ORGANIZER WORKER")
    print("===================================")
    print("Esta demo muestra el funcionamiento completo del OrganizerWorker:")
    print("1. Modo simulación (dry run)")
    print("2. Ejecución real con backups")
    print("3. Funcionamiento con threading")
    print()

    try:
        # Demo 1: Dry Run
        demo_dry_run()

        # Demo 2: Real Execution
        demo_real_execution()

        # Demo 3: Threading
        demo_threading()

        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("El OrganizerWorker ha demostrado:")
        print("✅ Organización automática de archivos por tipo")
        print("✅ Eliminación segura de archivos temporales")
        print("✅ Sistema de backups automático")
        print("✅ Callbacks para monitoreo de progreso")
        print("✅ Estadísticas detalladas de operación")
        print("✅ Historial de organizaciones")
        print("✅ Funcionamiento con threading en background")
        print("✅ Manejo robusto de errores")

    except KeyboardInterrupt:
        print("\n⚠️  Demo interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error en la demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
"""
Demo Organizer Worker
=====================

Demostración completa del OrganizerWorker mostrando:
- Organización de archivos por tipo
- Movimiento de archivos
- Eliminación de archivos temporales
- Sistema de backups
- Callbacks de organización
- Estadísticas y historial

Autor: BackendBot Team
Versión: 0.1.0
"""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from backendbot.packages.bots.base_bot import BotState
from backendbot.packages.bots.organizer_worker import OrganizerWorker


def create_test_files(base_dir: Path):
    """Crear archivos de prueba para la demostración."""
    print(f"📁 Creando archivos de prueba en: {base_dir}")

    # Crear archivos de diferentes tipos
    files_to_create = [
        ("document.pdf", "Contenido de un documento PDF"),
        ("presentation.pptx", "Contenido de una presentación PowerPoint"),
        ("spreadsheet.xlsx", "Datos de una hoja de cálculo"),
        ("photo.jpg", "Datos binarios de imagen JPEG"),
        ("diagram.png", "Datos binarios de diagrama PNG"),
        ("music.mp3", "Datos binarios de archivo MP3"),
        ("video.mp4", "Datos binarios de video MP4"),
        ("script.py", "print('Hola mundo')"),
        ("config.json", '{"setting": "value"}'),
        ("readme.md", "# Documentación"),
        ("temp.tmp", "Archivo temporal"),
        ("~backup.txt", "Archivo de backup temporal"),
        ("cache.dat", "Datos de caché"),
        ("log.txt", "Archivo de log de aplicación"),
    ]

    # Crear archivos grandes (más de 1MB) para pasar filtros
    large_content = "x" * (1024 * 1024 + 100)  # 1MB + 100 bytes

    for filename, content in files_to_create:
        file_path = base_dir / filename
        if filename.endswith((".jpg", ".png", ".mp3", ".mp4")):
            # Archivos binarios simulados
            file_path.write_bytes(large_content.encode("utf-8") + b"\x00\x01\x02")
        else:
            file_path.write_text(large_content + content)

    # Crear algunos archivos en subdirectorios
    sub_dir = base_dir / "project_files"
    sub_dir.mkdir()

    (sub_dir / "main.py").write_text(large_content + "def main(): pass")
    (sub_dir / "utils.py").write_text(large_content + "def helper(): pass")
    (sub_dir / "data.csv").write_text(large_content + "name,value\nitem1,100")

    print(f"✅ Creados {len(files_to_create) + 3} archivos de prueba")


def organization_callback(result):
    """Callback para mostrar resultados de organización."""
    print("\n📊 CALLBACK DE ORGANIZACIÓN:")
    print(f"   Procesados: {result.files_processed}")
    print(f"   Movidos: {result.files_moved}")
    print(f"   Eliminados: {result.files_deleted}")
    print(f"   Errores: {result.errors_count}")
    print(f"   Duración: {result.duration_seconds:.2f}s")
    if result.errors:
        print(f"   ⚠️  Errores encontrados: {len(result.errors)}")


def demo_dry_run():
    """Demostración en modo simulación (dry run)."""
    print("\n" + "=" * 60)
    print("🎭 DEMO 1: ORGANIZER WORKER - MODO SIMULACIÓN (DRY RUN)")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Crear archivos de prueba
        create_test_files(temp_path)

        # Configurar Organizer Worker
        config = {
            "scan_paths": [str(temp_path)],
            "dry_run": True,  # Modo simulación
            "organization_rules": {
                "by_type": True,
                "min_file_size_mb": 1,  # Solo archivos > 1MB
                "max_file_age_days": 365,  # Todos los archivos
                "auto_delete_temp": True,
            },
            "file_categories": {
                "documents": [".pdf", ".docx", ".txt", ".md"],
                "spreadsheets": [".xlsx", ".csv"],
                "images": [".jpg", ".png", ".gif"],
                "audio": [".mp3", ".wav"],
                "video": [".mp4", ".avi"],
                "code": [".py", ".js", ".html", ".css"],
                "temp": [".tmp", ".bak", ".cache"],
                "logs": [".log"],
            },
        }

        # Crear y configurar worker
        worker = OrganizerWorker(bot_id="demo-organizer", name="Demo Organizer")
        worker.config.update(config)

        # Agregar callback
        worker.add_organization_callback(organization_callback)

        print(f"\n🤖 Worker configurado: {worker}")
        print(f"📂 Directorios a escanear: {worker.scan_paths}")
        print(f"📋 Reglas: {worker.organization_rules}")

        # Ejecutar organización
        print("\n🚀 Ejecutando organización...")
        start_time = datetime.now()

        result = worker.execute_task()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"⏱️  Duración: {duration:.2f}s")
        print(f"✅ Éxito: {result['success']}")

        if result["success"]:
            stats = result["result"]
            print("\n📈 RESULTADOS:")
            print(f"   📁 Archivos procesados: {stats['files_processed']}")
            print(f"   📦 Archivos movidos: {stats['files_moved']}")
            print(f"   🗑️  Archivos eliminados: {stats['files_deleted']}")
            print(f"   ⚠️  Errores: {stats['errors_count']}")

            # Mostrar estructura final
            print("\n📂 ESTRUCTURA FINAL (SIMULADA):")
            show_directory_structure(temp_path)

        # Mostrar estadísticas
        print("\n📊 ESTADÍSTICAS DEL WORKER:")
        worker_stats = worker.get_statistics()
        for key, value in worker_stats.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")

        # Mostrar historial
        print("\n📚 HISTORIAL DE ORGANIZACIÓN:")
        history = worker.get_organization_history()
        for i, entry in enumerate(history[-3:], 1):  # Últimas 3 entradas
            print(
                f"   {i}. {entry['files_processed']} archivos, {entry['files_moved']} movidos"
            )


def demo_real_execution():
    """Demostración con ejecución real."""
    print("\n" + "=" * 60)
    print("🔥 DEMO 2: ORGANIZER WORKER - EJECUCIÓN REAL")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Crear archivos de prueba
        create_test_files(temp_path)

        # Configurar Organizer Worker para ejecución real
        config = {
            "scan_paths": [str(temp_path)],
            "dry_run": False,  # Ejecución real
            "organization_rules": {
                "by_type": True,
                "min_file_size_mb": 1,
                "max_file_age_days": 365,
                "auto_delete_temp": True,
            },
            "file_categories": {
                "documents": [".pdf", ".docx", ".txt", ".md"],
                "spreadsheets": [".xlsx", ".csv"],
                "images": [".jpg", ".png", ".gif"],
                "audio": [".mp3", ".wav"],
                "video": [".mp4", ".avi"],
                "code": [".py", ".js", ".html", ".css"],
                "temp": [".tmp", ".bak", ".cache"],
                "logs": [".log"],
            },
            "backup_dir": str(temp_path / "backups"),
        }

        # Crear y configurar worker
        worker = OrganizerWorker(
            bot_id="demo-organizer-real", name="Demo Organizer Real"
        )
        worker.config.update(config)

        # Agregar callback
        worker.add_organization_callback(organization_callback)

        print(f"\n🤖 Worker configurado: {worker}")
        print(f"📂 Directorios a escanear: {worker.scan_paths}")
        print(f"🔥 Modo: EJECUCIÓN REAL (archivos serán movidos/eliminados)")

        # Mostrar estructura inicial
        print("\n📂 ESTRUCTURA INICIAL:")
        show_directory_structure(temp_path)

        # Ejecutar organización
        print("\n🚀 Ejecutando organización REAL...")
        start_time = datetime.now()

        result = worker.execute_task()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"⏱️  Duración: {duration:.2f}s")
        print(f"✅ Éxito: {result['success']}")

        if result["success"]:
            stats = result["result"]
            print("\n📈 RESULTADOS:")
            print(f"   📁 Archivos procesados: {stats['files_processed']}")
            print(f"   📦 Archivos movidos: {stats['files_moved']}")
            print(f"   🗑️  Archivos eliminados: {stats['files_deleted']}")
            print(f"   ⚠️  Errores: {stats['errors_count']}")

            # Mostrar estructura final
            print("\n📂 ESTRUCTURA FINAL:")
            show_directory_structure(temp_path)

            # Verificar backups
            backup_dir = temp_path / "backups"
            if backup_dir.exists():
                backups = list(backup_dir.glob("*.bak"))
                print(f"\n💾 BACKUPS CREADOS: {len(backups)} archivos")
                for backup in backups[:3]:  # Mostrar primeros 3
                    print(f"   📄 {backup.name}")


def demo_threading():
    """Demostración de funcionamiento con threading."""
    print("\n" + "=" * 60)
    print("🧵 DEMO 3: ORGANIZER WORKER - THREADING")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Crear archivos de prueba
        create_test_files(temp_path)

        # Configurar worker con intervalo corto para demo
        config = {
            "scan_paths": [str(temp_path)],
            "dry_run": True,
            "organization_rules": {
                "by_type": True,
                "min_file_size_mb": 1,
                "max_file_age_days": 365,
                "auto_delete_temp": True,
            },
            "file_categories": {
                "documents": [".pdf", ".docx", ".txt", ".md"],
                "code": [".py", ".js"],
                "temp": [".tmp"],
            },
        }

        worker = OrganizerWorker(bot_id="demo-threading", name="Demo Threading")
        worker.config.update(config)

        print(f"🤖 Iniciando worker con threading: {worker}")
        print(f"⏰ Intervalo de ejecución: {worker.get_execution_interval()} segundos")

        # Iniciar worker
        worker.start()
        print(f"✅ Worker iniciado. Estado: {worker.state}")

        # Ejecutar tarea manualmente para demo
        print("\n🚀 Ejecutando tarea manualmente...")
        result = worker.execute_task()

        if result["success"]:
            stats = result["result"]
            print(
                f"✅ Organización completada: {stats['files_processed']} archivos procesados"
            )

        # Mostrar estado
        print(f"📊 Estado actual: {worker.state}")
        print(f"📈 Estadísticas: {worker.get_statistics()}")

        # Detener worker
        print("\n🛑 Deteniendo worker...")
        worker.stop()
        print(f"✅ Worker detenido. Estado final: {worker.state}")


def show_directory_structure(base_path: Path, indent: str = ""):
    """Mostrar estructura de directorios de forma recursiva."""
    try:
        for item in sorted(base_path.iterdir()):
            if item.is_file():
                size_mb = item.stat().st_size / (1024 * 1024)
                print(f"{indent}📄 {item.name} ({size_mb:.2f} MB)")
            elif item.is_dir() and not item.name.startswith("."):
                print(f"{indent}📁 {item.name}/")
                show_directory_structure(item, indent + "   ")
    except PermissionError:
        print(f"{indent}🔒 [Sin permisos]")


def main():
    """Función principal de la demo."""
    print("🎯 DEMO COMPLETA - ORGANIZER WORKER")
    print("===================================")
    print("Esta demo muestra el funcionamiento completo del OrganizerWorker:")
    print("1. Modo simulación (dry run)")
    print("2. Ejecución real con backups")
    print("3. Funcionamiento con threading")
    print()

    try:
        # Demo 1: Dry Run
        demo_dry_run()

        # Demo 2: Real Execution
        demo_real_execution()

        # Demo 3: Threading
        demo_threading()

        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("El OrganizerWorker ha demostrado:")
        print("✅ Organización automática de archivos por tipo")
        print("✅ Eliminación segura de archivos temporales")
        print("✅ Sistema de backups automático")
        print("✅ Callbacks para monitoreo de progreso")
        print("✅ Estadísticas detalladas de operación")
        print("✅ Historial de organizaciones")
        print("✅ Funcionamiento con threading en background")
        print("✅ Manejo robusto de errores")

    except KeyboardInterrupt:
        print("\n⚠️  Demo interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error en la demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
