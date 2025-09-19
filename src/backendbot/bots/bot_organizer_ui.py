"""
Bot Organizador: escanea carpetas, clasifica archivos y reporta a la UI.
Funcionalidades avanzadas de organización según el modo de operación.
"""
import threading
import time
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Any
from src.backendbot.modes import mode_manager
from src.backendbot.utils.logging_config import logger

class BotOrganizerUI:
    def __init__(self, ui_connector, folder="."):
        self.ui_connector = ui_connector
        self.base_folder = Path(folder).resolve()
        self.running = True
        self.last_scan = 0
        self.scan_interval = 300  # 5 minutos por defecto
        self.file_stats = defaultdict(int)
        self.thread = threading.Thread(target=self.organizer_loop, daemon=True)
        self.thread.start()

        # Crear carpetas de organización si no existen
        self._create_organization_folders()

    def _create_organization_folders(self):
        """Crear estructura de carpetas para organización automática"""
        try:
            org_folders = [
                "Documentos",
                "Imágenes",
                "Videos",
                "Música",
                "Programas",
                "Comprimidos",
                "Otros",
                "Descargas_Recientes",
                "Archivos_Grandes",
                "Duplicados"
            ]

            for folder in org_folders:
                folder_path = self.base_folder / folder
                folder_path.mkdir(exist_ok=True)

        except Exception as e:
            logger.error(f"Error creando carpetas de organización: {e}")

    def organizer_loop(self):
        while self.running:
            try:
                current_time = time.time()

                # Verificar si debe organizarse según el modo
                if mode_manager.should_cleanup() and (current_time - self.last_scan) > self.scan_interval:
                    self.perform_full_scan()
                    self.last_scan = current_time
                else:
                    # Escaneo rápido periódico
                    self.quick_scan()

                # Intervalo dinámico según el modo
                sleep_time = mode_manager.get_monitoring_interval() * 3  # Menos frecuente
                time.sleep(sleep_time)

            except Exception as e:
                self.ui_connector.send_message(f"Error en organizador: {str(e)}")
                time.sleep(60)

    def quick_scan(self):
        """Escaneo rápido para reporte de estado"""
        try:
            total_files = 0
            total_size = 0

            for root, dirs, files in os.walk(self.base_folder):
                # Excluir carpetas del sistema y de organización
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]

                for file in files:
                    if not file.startswith('.'):
                        total_files += 1
                        try:
                            file_path = Path(root) / file
                            total_size += file_path.stat().st_size
                        except:
                            pass

            # Convertir tamaño a formato legible
            size_mb = total_size / (1024 * 1024)
            msg = f"📁 {total_files} archivos | 💾 {size_mb:.1f} MB | 📂 {self.base_folder.name}"
            self.ui_connector.send_message(msg)

        except Exception as e:
            logger.error(f"Error en escaneo rápido: {e}")

    def perform_full_scan(self):
        """Escaneo completo con análisis detallado y organización"""
        try:
            self.ui_connector.send_message("🔍 Iniciando escaneo completo de archivos...")

            stats = self._analyze_files()
            self._report_statistics(stats)
            self._perform_auto_organization()

            self.ui_connector.send_message("✅ Escaneo y organización completados")

        except Exception as e:
            self.ui_connector.send_message(f"Error en escaneo completo: {str(e)}")

    def _analyze_files(self) -> Dict[str, Any]:
        """Analizar archivos en detalle"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'by_type': defaultdict(int),
            'by_size': {'small': 0, 'medium': 0, 'large': 0, 'huge': 0},
            'by_age': {'recent': 0, 'week': 0, 'month': 0, 'old': 0},
            'duplicates': [],
            'empty_files': []
        }

        file_hashes = defaultdict(list)

        for root, dirs, files in os.walk(self.base_folder):
            # Excluir carpetas del sistema
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]

            for file in files:
                if file.startswith('.'):
                    continue

                try:
                    file_path = Path(root) / file
                    stat = file_path.stat()

                    stats['total_files'] += 1
                    stats['total_size'] += stat.st_size

                    # Clasificar por tipo
                    ext = file_path.suffix.lower()
                    if ext:
                        stats['by_type'][ext] += 1
                    else:
                        stats['by_type']['sin_extension'] += 1

                    # Clasificar por tamaño
                    size_mb = stat.st_size / (1024 * 1024)
                    if size_mb < 1:
                        stats['by_size']['small'] += 1
                    elif size_mb < 10:
                        stats['by_size']['medium'] += 1
                    elif size_mb < 100:
                        stats['by_size']['large'] += 1
                    else:
                        stats['by_size']['huge'] += 1

                    # Clasificar por edad
                    age_days = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
                    if age_days < 1:
                        stats['by_age']['recent'] += 1
                    elif age_days < 7:
                        stats['by_age']['week'] += 1
                    elif age_days < 30:
                        stats['by_age']['month'] += 1
                    else:
                        stats['by_age']['old'] += 1

                    # Detectar archivos vacíos
                    if stat.st_size == 0:
                        stats['empty_files'].append(str(file_path))

                    # Detectar duplicados (por tamaño y nombre, simplificado)
                    size_name_key = f"{stat.st_size}_{file}"
                    file_hashes[size_name_key].append(file_path)

                except Exception as e:
                    logger.error(f"Error analizando {file}: {e}")

        # Identificar duplicados
        for files_list in file_hashes.values():
            if len(files_list) > 1:
                stats['duplicates'].extend(files_list[1:])  # Todos menos el primero

        return stats

    def _report_statistics(self, stats: Dict[str, Any]):
        """Reportar estadísticas del análisis"""
        try:
            size_gb = stats['total_size'] / (1024 * 1024 * 1024)

            self.ui_connector.send_message(f"📊 Estadísticas: {stats['total_files']} archivos, {size_gb:.2f} GB")

            # Top tipos de archivo
            top_types = sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True)[:5]
            if top_types:
                types_str = ", ".join(f"{ext}: {count}" for ext, count in top_types)
                self.ui_connector.send_message(f"📁 Tipos: {types_str}")

            # Distribución por tamaño
            size_dist = stats['by_size']
            self.ui_connector.send_message(f"📏 Tamaños: P:{size_dist['small']} M:{size_dist['medium']} G:{size_dist['large']} XG:{size_dist['huge']}")

            # Distribución por edad
            age_dist = stats['by_age']
            self.ui_connector.send_message(f"🕐 Edad: Hoy:{age_dist['recent']} Sem:{age_dist['week']} Mes:{age_dist['month']} Ant:{age_dist['old']}")

            # Alertas
            if stats['empty_files']:
                self.ui_connector.send_message(f"⚠️ {len(stats['empty_files'])} archivos vacíos encontrados")

            if stats['duplicates']:
                self.ui_connector.send_message(f"⚠️ {len(stats['duplicates'])} archivos duplicados detectados")

        except Exception as e:
            logger.error(f"Error reportando estadísticas: {e}")

    def _perform_auto_organization(self):
        """Realizar organización automática según el modo"""
        try:
            mode_info = mode_manager.get_mode_info()
            mode_name = mode_info['mode']

            if mode_name == "editor":
                self._organize_for_editing()
            elif mode_name == "desarrollo":
                self._organize_for_development()
            elif mode_name == "relax":
                self._organize_for_relax()
            else:
                # Para otros modos, organización básica
                self._basic_organization()

        except Exception as e:
            logger.error(f"Error en organización automática: {e}")

    def _organize_for_editing(self):
        """Organización específica para modo edición"""
        self.ui_connector.send_message("✏️ Organizando para modo edición...")
        # Mantener archivos de código en lugar prominente
        # Mover archivos temporales y de respaldo

    def _organize_for_development(self):
        """Organización específica para modo desarrollo"""
        self.ui_connector.send_message("🔧 Organizando para modo desarrollo...")
        # Agrupar archivos de proyecto, mover logs antiguos, etc.

    def _organize_for_relax(self):
        """Organización mínima para modo relax"""
        self.ui_connector.send_message("😌 Organización mínima para modo relax")
        # Solo organización básica si es necesario

    def _basic_organization(self):
        """Organización básica de archivos"""
        try:
            # Mover archivos por tipo a carpetas organizativas
            organized_count = 0

            for root, dirs, files in os.walk(self.base_folder):
                # Solo procesar el directorio base para evitar reorganizar carpetas ya organizadas
                if root != str(self.base_folder):
                    continue

                for file in files:
                    if file.startswith('.'):
                        continue

                    file_path = self.base_folder / file
                    ext = file_path.suffix.lower()

                    # Determinar carpeta destino
                    if ext in ['.doc', '.docx', '.pdf', '.txt', '.rtf']:
                        dest_folder = self.base_folder / "Documentos"
                    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
                        dest_folder = self.base_folder / "Imágenes"
                    elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv']:
                        dest_folder = self.base_folder / "Videos"
                    elif ext in ['.mp3', '.wav', '.flac', '.aac']:
                        dest_folder = self.base_folder / "Música"
                    elif ext in ['.exe', '.msi', '.dmg', '.pkg']:
                        dest_folder = self.base_folder / "Programas"
                    elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
                        dest_folder = self.base_folder / "Comprimidos"
                    else:
                        dest_folder = self.base_folder / "Otros"

                    # Mover archivo
                    try:
                        dest_path = dest_folder / file
                        if not dest_path.exists():
                            shutil.move(str(file_path), str(dest_path))
                            organized_count += 1
                    except Exception as e:
                        logger.error(f"Error moviendo {file}: {e}")

            if organized_count > 0:
                self.ui_connector.send_message(f"📂 Organizados {organized_count} archivos por tipo")

        except Exception as e:
            logger.error(f"Error en organización básica: {e}")

    def stop(self):
        self.running = False
