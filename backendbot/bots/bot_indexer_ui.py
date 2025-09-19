"""Bot Indexador: crea índice de archivos con búsqueda avanzada y reporta a la UI.
Funcionalidades inteligentes según el modo de operación.
"""

import json
import os
import threading
import time
from pathlib import Path
from typing import Any

from src.backendbot.modes import mode_manager
from src.backendbot.utils.logging_config import logger


class BotIndexerUI:
    def __init__(self, ui_connector, folder=".") -> None:
        self.ui_connector = ui_connector
        self.base_folder = Path(folder).resolve()
        self.running = True
        self.index_file = self.base_folder / ".backendbot_index.json"
        self.file_index = {}
        self.search_cache = {}
        self.last_index_update = 0
        self.index_interval = 600  # 10 minutos por defecto
        self.thread = threading.Thread(target=self.indexer_loop, daemon=True)
        self.thread.start()

        # Cargar índice existente si existe
        self._load_index()

    def indexer_loop(self):
        while self.running:
            try:
                current_time = time.time()

                # Actualizar índice periódicamente
                if (current_time - self.last_index_update) > self.index_interval:
                    self._update_index()
                    self.last_index_update = current_time
                else:
                    # Verificación rápida de cambios
                    self._quick_check()

                # Procesar búsquedas pendientes según el modo
                self._process_mode_specific_tasks()

                # Intervalo dinámico según el modo
                sleep_time = mode_manager.get_monitoring_interval() * 2
                time.sleep(sleep_time)

            except Exception as e:
                self.ui_connector.send_message(f"Error en indexador: {str(e)}")
                time.sleep(60)

    def _update_index(self):
        """Actualizar el índice completo de archivos."""
        try:
            self.ui_connector.send_message("🔍 Actualizando índice de archivos...")

            new_index = {}
            total_files = 0
            total_size = 0

            for root, dirs, files in os.walk(self.base_folder):
                # Excluir carpetas del sistema
                dirs[:] = [
                    d
                    for d in dirs
                    if not d.startswith(".")
                    and d not in ["__pycache__", "node_modules"]
                ]

                for file in files:
                    if file.startswith("."):
                        continue

                    try:
                        file_path = Path(root) / file
                        stat = file_path.stat()

                        # Crear entrada de índice
                        entry = {
                            "name": file,
                            "path": str(file_path),
                            "relative_path": str(
                                file_path.relative_to(self.base_folder)
                            ),
                            "size": stat.st_size,
                            "modified": stat.st_mtime,
                            "created": stat.st_ctime,
                            "extension": file_path.suffix.lower(),
                            "is_hidden": file.startswith("."),
                            "directory": str(Path(root).relative_to(self.base_folder)),
                        }

                        # Agregar metadatos adicionales según tipo de archivo
                        self._add_file_metadata(entry, file_path)

                        new_index[str(file_path)] = entry
                        total_files += 1
                        total_size += stat.st_size

                    except Exception as e:
                        logger.error(f"Error indexando {file}: {e}")

            self.file_index = new_index
            self._save_index()

            size_mb = total_size / (1024 * 1024)
            self.ui_connector.send_message(
                f"✅ Índice actualizado: {total_files} archivos, {size_mb:.1f} MB"
            )

        except Exception as e:
            logger.error(f"Error actualizando índice: {e}")

    def _add_file_metadata(self, entry: dict[str, Any], file_path: Path):
        """Agregar metadatos específicos según tipo de archivo."""
        try:
            ext = entry["extension"]

            # Archivos de código
            if ext in [
                ".py",
                ".js",
                ".ts",
                ".java",
                ".cpp",
                ".c",
                ".cs",
                ".php",
                ".rb",
                ".go",
            ]:
                entry["type"] = "code"
                entry["language"] = ext[1:]
                # Contar líneas (simplificado)
                try:
                    with open(file_path, encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        entry["lines"] = len(lines)
                        entry["code_lines"] = len(
                            [
                                l
                                for l in lines
                                if l.strip() and not l.strip().startswith("#")
                            ]
                        )
                except:
                    entry["lines"] = 0

            # Archivos de documento
            elif ext in [".txt", ".md", ".doc", ".docx", ".pdf"]:
                entry["type"] = "document"
                try:
                    with open(file_path, encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        entry["word_count"] = len(content.split())
                        entry["char_count"] = len(content)
                except:
                    pass

            # Imágenes
            elif ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]:
                entry["type"] = "image"

            # Videos
            elif ext in [".mp4", ".avi", ".mkv", ".mov", ".wmv"]:
                entry["type"] = "video"

            # Música
            elif ext in [".mp3", ".wav", ".flac", ".aac"]:
                entry["type"] = "audio"

            else:
                entry["type"] = "other"

        except Exception as e:
            logger.error(f"Error agregando metadatos para {file_path}: {e}")

    def _quick_check(self):
        """Verificación rápida de cambios en archivos."""
        try:
            # Contar archivos totales para reporte rápido
            total_files = sum(
                1
                for _, _, files in os.walk(self.base_folder)
                for f in files
                if not f.startswith(".")
            )

            indexed_files = len(self.file_index)
            msg = f"📇 Índice: {indexed_files} archivos indexados"

            if total_files != indexed_files:
                msg += f" (⚠️ {abs(total_files - indexed_files)} cambios detectados)"

            self.ui_connector.send_message(msg)

        except Exception as e:
            logger.error(f"Error en verificación rápida: {e}")

    def _process_mode_specific_tasks(self):
        """Procesar tareas específicas según el modo actual."""
        try:
            mode_info = mode_manager.get_mode_info()
            mode_name = mode_info["mode"]

            if mode_name == "editor":
                self._editor_mode_tasks()
            elif mode_name == "desarrollo":
                self._development_mode_tasks()
            elif mode_name == "streaming":
                self._streaming_mode_tasks()
            elif mode_name == "gaming":
                self._gaming_mode_tasks()

        except Exception as e:
            logger.error(f"Error en tareas específicas del modo: {e}")

    def _editor_mode_tasks(self):
        """Tareas específicas para modo edición."""
        # Buscar archivos de código recientes
        recent_code = self._find_recent_files_by_type("code", hours=24)
        if recent_code:
            self.ui_connector.send_message(
                f"💻 {len(recent_code)} archivos de código modificados recientemente"
            )

    def _development_mode_tasks(self):
        """Tareas específicas para modo desarrollo."""
        # Buscar archivos de configuración y proyecto
        config_files = self._find_files_by_pattern(
            ["package.json", "requirements.txt", "setup.py", "Dockerfile"]
        )
        if config_files:
            self.ui_connector.send_message(
                f"🔧 {len(config_files)} archivos de configuración encontrados"
            )

    def _streaming_mode_tasks(self):
        """Tareas específicas para modo streaming."""
        # Minimizar reportes para no interferir
        pass

    def _gaming_mode_tasks(self):
        """Tareas específicas para modo gaming."""
        # Reportes mínimos
        pass

    def _find_recent_files_by_type(
        self, file_type: str, hours: int = 24
    ) -> list[dict[str, Any]]:
        """Encontrar archivos recientes por tipo."""
        cutoff_time = time.time() - (hours * 3600)
        recent_files = []

        for entry in self.file_index.values():
            if (
                entry.get("type") == file_type
                and entry.get("modified", 0) > cutoff_time
            ):
                recent_files.append(entry)

        return recent_files

    def _find_files_by_pattern(self, patterns: list[str]) -> list[dict[str, Any]]:
        """Encontrar archivos por patrones de nombre."""
        matches = []

        for entry in self.file_index.values():
            name = entry.get("name", "").lower()
            if any(pattern.lower() in name for pattern in patterns):
                matches.append(entry)

        return matches

    def search_files(self, query: str, file_type: str = None) -> list[dict[str, Any]]:
        """Buscar archivos por consulta."""
        results = []
        query_lower = query.lower()

        for entry in self.file_index.values():
            # Búsqueda por nombre
            if query_lower in entry.get("name", "").lower():
                results.append(entry)
                continue

            # Búsqueda por tipo si se especifica
            if file_type and entry.get("type") != file_type:
                continue

            # Búsqueda por contenido (simplificada para archivos de texto)
            if entry.get("type") in ["code", "document"]:
                # Aquí se podría implementar búsqueda de contenido
                pass

        return results[:50]  # Limitar resultados

    def _load_index(self):
        """Cargar índice desde archivo."""
        try:
            if self.index_file.exists():
                with open(self.index_file, encoding="utf-8") as f:
                    self.file_index = json.load(f)
                logger.info(f"Índice cargado: {len(self.file_index)} archivos")
        except Exception as e:
            logger.error(f"Error cargando índice: {e}")
            self.file_index = {}

    def _save_index(self):
        """Guardar índice en archivo."""
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self.file_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando índice: {e}")

    def stop(self):
        self.running = False
        self._save_index()
