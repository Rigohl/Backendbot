"""Bot Auditor de Archivos: detecta archivos problemáticos y realiza auditorías inteligentes.
Funcionalidades avanzadas según el modo de operación.
"""

import os
import shutil
import threading
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from src.backendbot.modes import mode_manager
from src.backendbot.utils.logging_config import logger


class BotAuditorFilesUI:
    def __init__(self, ui_connector, folder=".", months=6) -> None:
        self.ui_connector = ui_connector
        self.base_folder = Path(folder).resolve()
        self.months_threshold = months
        self.running = True
        self.last_audit = 0
        self.audit_interval = 1800  # 30 minutos por defecto
        self.risk_assessment = defaultdict(list)
        self.thread = threading.Thread(target=self.audit_loop, daemon=True)
        self.thread.start()

    def audit_loop(self):
        while self.running:
            try:
                current_time = time.time()

                # Realizar auditoría completa periódicamente
                if (current_time - self.last_audit) > self.audit_interval:
                    self.perform_comprehensive_audit()
                    self.last_audit = current_time
                else:
                    # Verificación rápida
                    self.quick_audit_check()

                # Procesar acciones automáticas según el modo
                self._process_automated_actions()

                # Intervalo dinámico según el modo
                sleep_time = (
                    mode_manager.get_monitoring_interval() * 4
                )  # Menos frecuente
                time.sleep(sleep_time)

            except Exception as e:
                self.ui_connector.send_message(
                    f"Error en auditor de archivos: {str(e)}"
                )
                time.sleep(120)

    def perform_comprehensive_audit(self):
        """Realizar auditoría completa de archivos."""
        try:
            self.ui_connector.send_message(
                "🔍 Iniciando auditoría completa de archivos..."
            )

            audit_results = self._analyze_file_health()
            self._assess_risks(audit_results)
            self._generate_audit_report(audit_results)

            self.ui_connector.send_message("✅ Auditoría de archivos completada")

        except Exception as e:
            logger.error(f"Error en auditoría completa: {e}")

    def _analyze_file_health(self) -> dict[str, Any]:
        """Analizar la salud de los archivos."""
        results = {
            "old_files": [],
            "large_files": [],
            "empty_files": [],
            "duplicate_files": defaultdict(list),
            "corrupt_files": [],
            "temp_files": [],
            "cache_files": [],
            "log_files": [],
            "total_analyzed": 0,
            "total_size": 0,
        }

        file_sizes = defaultdict(list)  # Para detectar duplicados por tamaño

        for root, dirs, files in os.walk(self.base_folder):
            # Excluir carpetas del sistema
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".") and d not in ["__pycache__", "node_modules"]
            ]

            for file in files:
                if file.startswith("."):
                    continue

                try:
                    file_path = Path(root) / file
                    stat = file_path.stat()

                    results["total_analyzed"] += 1
                    results["total_size"] += stat.st_size

                    # Archivos antiguos (no accedidos)
                    days_since_access = (
                        datetime.now() - datetime.fromtimestamp(stat.st_atime)
                    ).days
                    if days_since_access > (self.months_threshold * 30):
                        results["old_files"].append(
                            {
                                "path": str(file_path),
                                "days_since_access": days_since_access,
                                "size": stat.st_size,
                            }
                        )

                    # Archivos grandes (>100MB)
                    if stat.st_size > 100 * 1024 * 1024:
                        results["large_files"].append(
                            {
                                "path": str(file_path),
                                "size": stat.st_size,
                                "size_mb": stat.st_size / (1024 * 1024),
                            }
                        )

                    # Archivos vacíos
                    if stat.st_size == 0:
                        results["empty_files"].append(str(file_path))

                    # Detectar duplicados por tamaño y nombre
                    size_name_key = f"{stat.st_size}_{file}"
                    file_sizes[size_name_key].append(file_path)

                    # Clasificar por tipo problemático
                    if self._is_temp_file(file):
                        results["temp_files"].append(str(file_path))
                    elif self._is_cache_file(file):
                        results["cache_files"].append(str(file_path))
                    elif self._is_log_file(file):
                        results["log_files"].append(str(file_path))

                except Exception as e:
                    results["corrupt_files"].append(str(file_path))
                    logger.error(f"Error analizando {file}: {e}")

        # Procesar duplicados
        for files_list in file_sizes.values():
            if len(files_list) > 1:
                results["duplicate_files"][str(files_list[0])].extend(
                    str(f) for f in files_list[1:]
                )

        return results

    def _is_temp_file(self, filename: str) -> bool:
        """Determinar si es un archivo temporal."""
        temp_patterns = ["temp", "tmp", "~", "backup", ".bak", ".tmp", ".temp"]
        filename_lower = filename.lower()
        return any(pattern in filename_lower for pattern in temp_patterns)

    def _is_cache_file(self, filename: str) -> bool:
        """Determinar si es un archivo de caché."""
        cache_patterns = ["cache", ".cache", "thumbs.db", "desktop.ini"]
        filename_lower = filename.lower()
        return any(pattern in filename_lower for pattern in cache_patterns)

    def _is_log_file(self, filename: str) -> bool:
        """Determinar si es un archivo de log."""
        log_patterns = [".log", "log.", "debug", "error", "trace"]
        filename_lower = filename.lower()
        return any(pattern in filename_lower for pattern in log_patterns)

    def _assess_risks(self, audit_results: dict[str, Any]):
        """Evaluar riesgos de los archivos encontrados."""
        self.risk_assessment.clear()

        # Alto riesgo
        self.risk_assessment["high"].extend(audit_results["corrupt_files"])
        self.risk_assessment["high"].extend(audit_results["duplicate_files"].keys())

        # Riesgo medio
        large_old_files = [
            f for f in audit_results["large_files"] if f["days_since_access"] > 90
        ]
        self.risk_assessment["medium"].extend(f["path"] for f in large_old_files)

        # Riesgo bajo
        self.risk_assessment["low"].extend(audit_results["temp_files"])
        self.risk_assessment["low"].extend(audit_results["cache_files"])
        self.risk_assessment["low"].extend(audit_results["empty_files"])

    def _generate_audit_report(self, audit_results: dict[str, Any]):
        """Generar reporte de auditoría."""
        try:
            total_size_gb = audit_results["total_size"] / (1024 * 1024 * 1024)

            self.ui_connector.send_message(
                f"📊 Auditoría: {audit_results['total_analyzed']} archivos, {total_size_gb:.2f} GB"
            )

            # Reportar problemas encontrados
            if audit_results["old_files"]:
                self.ui_connector.send_message(
                    f"🕰️ {len(audit_results['old_files'])} archivos antiguos (> {self.months_threshold} meses)"
                )

            if audit_results["large_files"]:
                total_large_size = sum(f["size"] for f in audit_results["large_files"])
                large_size_gb = total_large_size / (1024 * 1024 * 1024)
                self.ui_connector.send_message(
                    f"📁 {len(audit_results['large_files'])} archivos grandes ({large_size_gb:.2f} GB)"
                )

            if audit_results["empty_files"]:
                self.ui_connector.send_message(
                    f"📄 {len(audit_results['empty_files'])} archivos vacíos"
                )

            if audit_results["duplicate_files"]:
                total_duplicates = sum(
                    len(files) for files in audit_results["duplicate_files"].values()
                )
                self.ui_connector.send_message(
                    f"🔄 {total_duplicates} archivos duplicados"
                )

            if audit_results["corrupt_files"]:
                self.ui_connector.send_message(
                    f"⚠️ {len(audit_results['corrupt_files'])} archivos corruptos"
                )

            # Reportar archivos temporales/cache
            temp_cache_count = len(audit_results["temp_files"]) + len(
                audit_results["cache_files"]
            )
            if temp_cache_count > 0:
                self.ui_connector.send_message(
                    f"🗑️ {temp_cache_count} archivos temporales/cache"
                )

        except Exception as e:
            logger.error(f"Error generando reporte: {e}")

    def _process_automated_actions(self):
        """Procesar acciones automáticas según el modo y configuración."""
        try:
            if not mode_manager.should_cleanup():
                return  # No realizar acciones automáticas si no está habilitado

            mode_info = mode_manager.get_mode_info()
            mode_name = mode_info["mode"]

            if mode_name in ["desarrollo", "editor"]:
                self._aggressive_cleanup()
            elif mode_name == "relax":
                self._conservative_cleanup()
            else:
                self._moderate_cleanup()

        except Exception as e:
            logger.error(f"Error en acciones automáticas: {e}")

    def _aggressive_cleanup(self):
        """Limpieza agresiva para modos de desarrollo/edición."""
        try:
            cleaned_count = 0

            # Limpiar archivos temporales agresivamente
            for risk_level in ["low", "medium"]:
                for file_path in self.risk_assessment[risk_level]:
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            cleaned_count += 1
                    except Exception as e:
                        logger.error(f"Error eliminando {file_path}: {e}")

            if cleaned_count > 0:
                self.ui_connector.send_message(
                    f"🧹 Limpieza agresiva: {cleaned_count} archivos eliminados"
                )

        except Exception as e:
            logger.error(f"Error en limpieza agresiva: {e}")

    def _moderate_cleanup(self):
        """Limpieza moderada para modos normales."""
        try:
            # Solo limpiar archivos de bajo riesgo automáticamente
            cleaned_count = 0

            for file_path in self.risk_assessment["low"]:
                try:
                    if os.path.exists(file_path):
                        # Mover a papelera en lugar de eliminar
                        self._move_to_recycle_bin(file_path)
                        cleaned_count += 1
                except Exception as e:
                    logger.error(f"Error moviendo {file_path}: {e}")

            if cleaned_count > 0:
                self.ui_connector.send_message(
                    f"🗑️ Limpieza moderada: {cleaned_count} archivos movidos a papelera"
                )

        except Exception as e:
            logger.error(f"Error en limpieza moderada: {e}")

    def _conservative_cleanup(self):
        """Limpieza conservadora para modo relax."""
        # Solo reportar, no eliminar automáticamente
        total_risky = sum(len(files) for files in self.risk_assessment.values())
        if total_risky > 0:
            self.ui_connector.send_message(
                f"ℹ️ {total_risky} archivos candidatos para limpieza (modo conservador)"
            )

    def _move_to_recycle_bin(self, file_path: str):
        """Mover archivo a papelera (simulado)."""
        try:
            # En un sistema real, usaríamos send2trash o similar
            # Por ahora, solo movemos a una carpeta de respaldo
            recycle_dir = self.base_folder / "Papelera_BackendBot"
            recycle_dir.mkdir(exist_ok=True)

            file_obj = Path(file_path)
            dest_path = recycle_dir / file_obj.name

            # Evitar sobrescribir
            counter = 1
            while dest_path.exists():
                stem = file_obj.stem
                suffix = file_obj.suffix
                dest_path = recycle_dir / f"{stem}_{counter}{suffix}"
                counter += 1

            shutil.move(file_path, dest_path)
            logger.info(f"Archivo movido a papelera: {file_path} -> {dest_path}")

        except Exception as e:
            logger.error(f"Error moviendo a papelera {file_path}: {e}")

    def quick_audit_check(self):
        """Verificación rápida de archivos problemáticos."""
        try:
            # Conteo rápido de archivos potencialmente problemáticos
            old_count = 0
            large_count = 0

            for root, dirs, files in os.walk(self.base_folder):
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

                        # Verificar antigüedad
                        days_since_access = (
                            datetime.now() - datetime.fromtimestamp(stat.st_atime)
                        ).days
                        if days_since_access > (self.months_threshold * 30):
                            old_count += 1

                        # Verificar tamaño
                        if stat.st_size > 100 * 1024 * 1024:
                            large_count += 1

                    except:
                        pass

            if old_count > 0 or large_count > 0:
                msg = f"🔍 Auditor: {old_count} antiguos, {large_count} grandes"
                self.ui_connector.send_message(msg)

        except Exception as e:
            logger.error(f"Error en verificación rápida: {e}")

    def stop(self):
        self.running = False
