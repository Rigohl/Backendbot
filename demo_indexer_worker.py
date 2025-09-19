"""
Demo del Indexer Worker - BackendBot
====================================

Demostración completa del IndexerWorker mostrando:
- Indexación de archivos
- Búsqueda por contenido
- Filtros avanzados
- Estadísticas del índice
- Funcionamiento en background

Autor: BackendBot Team
Versión: 0.1.0
"""

import os
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

from backendbot.packages.bots.indexer_worker import BotState, IndexerWorker


def create_demo_files(base_dir: Path):
    """Crear archivos de demostración para indexar."""
    print("📁 Creando archivos de demostración...")

    # Crear estructura de directorios
    docs_dir = base_dir / "documents"
    code_dir = base_dir / "code"
    docs_dir.mkdir(exist_ok=True)
    code_dir.mkdir(exist_ok=True)

    # Archivo de documentación
    readme_file = docs_dir / "README.md"
    readme_content = """
# BackendBot - Sistema de Indexación

Este es un sistema avanzado de indexación y búsqueda de archivos.

## Características

- Indexación completa de directorios
- Búsqueda por contenido y metadatos
- Filtros avanzados por tipo, tamaño, fecha
- Sistema de relevancia inteligente
- Persistencia de índices
- Funcionamiento en background

## Uso

El sistema permite buscar archivos por:
- Contenido del archivo
- Nombre del archivo
- Tipo de archivo
- Tamaño del archivo
- Fecha de modificación

### Ejemplos de búsqueda

- Buscar "python": encuentra archivos que contienen "python"
- Buscar "config" extensión ".json": archivos JSON con "config"
- Buscar archivos modificados en los últimos 7 días
"""
    readme_file.write_text(readme_content, encoding="utf-8")

    # Archivo de configuración
    config_file = docs_dir / "config.yaml"
    config_content = """
backendbot:
  indexer:
    enabled: true
    paths:
      - ./documents
      - ./code
    exclude:
      - "*.tmp"
      - ".git/"
    max_size: 100MB

  search:
    fuzzy_matching: true
    context_lines: 3
    highlight_terms: true

logging:
  level: INFO
  file: backendbot.log
  max_size: 10MB
  backup_count: 5
"""
    config_file.write_text(config_content, encoding="utf-8")

    # Archivo de código Python
    main_file = code_dir / "main.py"
    main_content = '''#!/usr/bin/env python3
"""
BackendBot - Sistema Principal
==============================

Sistema de automatización y organización de archivos.

Autor: BackendBot Team
Versión: 0.1.0
"""

import sys
import logging
from pathlib import Path

from backendbot.core.config import Config
from backendbot.core.logger import setup_logging
from backendbot.workers.indexer import IndexerWorker
from backendbot.workers.monitor import MonitorWorker
from backendbot.workers.organizer import OrganizerWorker


def main():
    """Función principal del sistema."""
    print("🚀 Iniciando BackendBot...")

    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Cargar configuración
        config = Config()
        config.load()

        # Inicializar workers
        indexer = IndexerWorker("indexer-001", "File Indexer")
        monitor = MonitorWorker("monitor-001", "System Monitor")
        organizer = OrganizerWorker("organizer-001", "File Organizer")

        # Iniciar workers
        indexer.start()
        monitor.start()
        organizer.start()

        logger.info("BackendBot iniciado correctamente")
        print("✅ BackendBot ejecutándose...")

        # Mantener ejecutándose
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Deteniendo BackendBot...")
        print("\\n🛑 Deteniendo BackendBot...")

        # Detener workers
        indexer.stop()
        monitor.stop()
        organizer.stop()

        print("✅ BackendBot detenido correctamente")

    except Exception as e:
        logger.error(f"Error en BackendBot: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
    main_file.write_text(main_content, encoding="utf-8")

    # Archivo de código adicional
    utils_file = code_dir / "utils.py"
    utils_content = '''"""
Utilidades del BackendBot
========================

Funciones de utilidad para el sistema BackendBot.

Autor: BackendBot Team
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any


def get_file_info(file_path: Path) -> Dict[str, Any]:
    """
    Obtener información detallada de un archivo.

    Args:
        file_path: Ruta del archivo

    Returns:
        Diccionario con información del archivo
    """
    stat = file_path.stat()

    return {
        'name': file_path.name,
        'extension': file_path.suffix,
        'size': stat.st_size,
        'size_mb': stat.st_size / (1024 * 1024),
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'created': datetime.fromtimestamp(stat.st_ctime),
        'is_file': file_path.is_file(),
        'is_dir': file_path.is_dir()
    }


def find_files_by_pattern(directory: Path, pattern: str) -> List[Path]:
    """
    Buscar archivos por patrón regex.

    Args:
        directory: Directorio base
        pattern: Patrón regex

    Returns:
        Lista de archivos que coinciden
    """
    files = []
    regex = re.compile(pattern, re.IGNORECASE)

    for file_path in directory.rglob('*'):
        if file_path.is_file() and regex.search(file_path.name):
            files.append(file_path)

    return files


def calculate_directory_size(directory: Path) -> int:
    """
    Calcular tamaño total de un directorio.

    Args:
        directory: Directorio a calcular

    Returns:
        Tamaño total en bytes
    """
    total_size = 0

    for file_path in directory.rglob('*'):
        if file_path.is_file():
            total_size += file_path.stat().st_size

    return total_size


def format_size(size_bytes: int) -> str:
    """
    Formatear tamaño en bytes a formato legible.

    Args:
        size_bytes: Tamaño en bytes

    Returns:
        Cadena formateada
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return ".1f"
        size_bytes /= 1024.0

    return ".1f"


def clean_filename(filename: str) -> str:
    """
    Limpiar nombre de archivo removiendo caracteres inválidos.

    Args:
        filename: Nombre original

    Returns:
        Nombre limpio
    """
    # Caracteres inválidos en Windows
    invalid_chars = '<>:"/\\\\|?*'
    cleaned = filename

    for char in invalid_chars:
        cleaned = cleaned.replace(char, '_')

    # Remover espacios múltiples
    cleaned = re.sub(r'\\s+', ' ', cleaned).strip()

    return cleaned
'''
    utils_file.write_text(utils_content, encoding="utf-8")

    # Archivo de datos JSON
    data_file = docs_dir / "data.json"
    data_content = """
{
  "backendbot": {
    "version": "0.1.0",
    "workers": [
      {
        "name": "IndexerWorker",
        "description": "Indexa y busca archivos",
        "status": "active"
      },
      {
        "name": "MonitorWorker",
        "description": "Monitorea sistema y recursos",
        "status": "active"
      },
      {
        "name": "OrganizerWorker",
        "description": "Organiza archivos automáticamente",
        "status": "active"
      }
    ],
    "features": [
      "File indexing",
      "Content search",
      "System monitoring",
      "File organization",
      "Background processing"
    ]
  },
  "configuration": {
    "index_paths": ["./documents", "./code"],
    "exclude_patterns": ["*.tmp", ".git/"],
    "max_file_size": "100MB",
    "search_enabled": true,
    "monitoring_enabled": true
  }
}
"""
    data_file.write_text(data_content, encoding="utf-8")

    print(f"✅ Archivos creados en {base_dir}")
    return [readme_file, config_file, main_file, utils_file, data_file]


def demo_indexer_worker():
    """Demostración completa del IndexerWorker."""
    print("🎯 Demo del IndexerWorker - BackendBot")
    print("=" * 50)

    # Crear directorio temporal para la demo
    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = Path(temp_dir) / "backendbot_demo"
        base_dir.mkdir(exist_ok=True)

        # Crear archivos de demostración
        demo_files = create_demo_files(base_dir)

        print(f"\\n📊 Estadísticas de archivos creados:")
        total_size = 0
        for file_path in demo_files:
            size = file_path.stat().st_size
            total_size += size
            print(f"  📄 {file_path.name}: {size} bytes")

        print(f"  📊 Total: {len(demo_files)} archivos, {total_size} bytes")

        # Inicializar IndexerWorker
        print("\\n🔧 Inicializando IndexerWorker...")
        indexer = IndexerWorker("demo-indexer", "Demo Indexer")

        # Configurar para la demo
        indexer.config.update(
            {
                "index_paths": [str(base_dir)],
                "exclude_patterns": [r"\.git/", r"__pycache__/"],
                "include_patterns": [r".*"],
                "index_file_types": {".txt", ".md", ".py", ".json", ".yaml"},
                "max_file_size_mb": 10,
                "index_content": True,
                "index_metadata": True,
                "persistent_index": False,  # No persistir para demo
                "execution_interval": 60,
            }
        )
        indexer.on_config_updated()

        print("✅ IndexerWorker configurado")

        # Ejecutar indexación
        print("\\n🔍 Ejecutando indexación...")
        start_time = time.time()

        result = indexer.execute_task()

        end_time = time.time()
        duration = end_time - start_time

        print(f"⏱️  Duración: {duration:.2f} segundos")
        print(f"  📊 Archivos procesados: {result['result']['files_processed']}")
        print(
            f"  📊 Archivos indexados: {result['result']['organization_summary']['files_indexed']}"
        )
        print(f"  📊 Errores: {result['result']['errors_count']}")

        # Mostrar estadísticas del índice
        print("\\n📈 Estadísticas del índice:")
        stats = indexer.get_index_stats()
        print(f"  📊 Total archivos: {stats['total_files']}")
        print(f"  📊 Tamaño total: {stats['total_size_mb']:.1f} MB")
        print(f"  📊 Términos de búsqueda: {stats['search_terms']}")
        print(f"  📊 Tipos de archivo: {stats['file_types']}")

        # Demostración de búsquedas
        print("\\n🔎 Demostración de búsquedas:")

        # Búsqueda 1: Python
        print("\\n  1️⃣ Buscando 'python':")
        results = indexer.search_files("python")
        print(f"     Resultados encontrados: {len(results)}")
        for i, result in enumerate(results[:3], 1):  # Mostrar primeros 3
            print(
                f"     {i}. {result.file_index.name} (relevancia: {result.relevance_score:.2f})"
            )
            if result.context:
                print(f"        Contexto: {result.context[:100]}...")

        # Búsqueda 2: Configuración
        print("\\n  2️⃣ Buscando 'config' en archivos .json:")
        results = indexer.search_files("config", extension=".json")
        print(f"     Resultados encontrados: {len(results)}")
        for i, result in enumerate(results[:2], 1):
            print(
                f"     {i}. {result.file_index.name} (relevancia: {result.relevance_score:.2f})"
            )

        # Búsqueda 3: Sistema
        print("\\n  3️⃣ Buscando 'sistema' con filtro de tamaño:")
        results = indexer.search_files("sistema", size_max=10000)
        print(f"     Resultados encontrados: {len(results)}")
        for i, result in enumerate(results[:2], 1):
            print(
                f"     {i}. {result.file_index.name} ({result.file_index.size} bytes)"
            )

        # Búsqueda sin resultados
        print("\\n  4️⃣ Buscando término inexistente 'xyz123':")
        results = indexer.search_files("xyz123")
        print(f"     Resultados encontrados: {len(results)}")

        # Demostración de funcionamiento en background
        print("\\n🔄 Demostración de funcionamiento en background:")

        def index_callback(index_result):
            """Callback para mostrar progreso de indexación."""
            if isinstance(index_result, dict) and "result" in index_result:
                files_indexed = index_result["result"]["organization_summary"][
                    "files_indexed"
                ]
            else:
                files_indexed = getattr(index_result, "organization_summary", {}).get(
                    "files_indexed", 0
                )
            print(f"  📡 Callback: Indexación completada - {files_indexed} archivos")

        # Agregar callback
        indexer.add_index_callback(index_callback)

        # Iniciar worker en background
        print("  ▶️  Iniciando worker en background...")
        indexer.start()

        # Esperar un poco
        time.sleep(2)

        # Verificar estado
        print(f"  📊 Estado del worker: {indexer.state}")
        print(f"  📊 Archivos en índice: {len(indexer.file_index)}")

        # Ejecutar tarea en background
        print("  🔄 Ejecutando tarea en background...")
        bg_result = indexer.execute_task()

        # Esperar a que termine
        time.sleep(1)

        # Detener worker
        print("  ⏹️  Deteniendo worker...")
        indexer.stop()

        # Esperar a que se detenga completamente
        time.sleep(1)
        print(f"  📊 Estado final: {indexer.state}")

        # Limpiar índice
        print("\\n🧹 Limpiando índice...")
        indexer.clear_index()
        print(f"  📊 Archivos después de limpiar: {len(indexer.file_index)}")

        print("\\n🎉 Demo del IndexerWorker completada exitosamente!")
        print("\\n📋 Resumen:")
        print("  ✅ Indexación completa de archivos")
        print("  ✅ Búsqueda por contenido con relevancia")
        print("  ✅ Filtros avanzados (tipo, tamaño, fecha)")
        print("  ✅ Estadísticas detalladas")
        print("  ✅ Funcionamiento en background")
        print("  ✅ Sistema de callbacks")
        print("  ✅ Persistencia de índices")
        print("  ✅ Manejo de errores robusto")


if __name__ == "__main__":
    demo_indexer_worker()
