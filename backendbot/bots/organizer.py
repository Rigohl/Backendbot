"""Bot Organizer - Organiza archivos y carpetas."""

from backendbot.core.di.container import container
from backendbot.core.bot_base import BaseBot
import os
import shutil
from pathlib import Path


class OrganizerBot(BaseBot):
    """Bot Organizer - Organiza archivos y carpetas."""

    def __init__(self) -> None:
        super().__init__(name="organizer")
        self.logger = container.get_logger()
        self.config = container.get_config_manager()
        self.data_repo = container.get_data_repository()

        # Extensiones por categoría
        self.file_categories = {
            'Documentos': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
            'Imágenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'Música': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
            'Archivos': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'Programas': ['.exe', '.msi', '.dmg', '.deb', '.rpm', '.app'],
            'Código': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb', '.go'],
        }

    def execute(self, action: str) -> str:
        """Ejecutar acción del organizer."""
        if action == "status":
            return "📁 Organizer listo para organizar archivos"

        elif action == "organize" or action == "organize_by_type":
            result = self._organize_by_type()
            try:
                self.record_result("organize", {"result": result})
            except Exception:
                pass
            return result

        elif action == "scan":
            result = self._scan_and_organize()
            try:
                self.record_result("scan", {"result": result})
            except Exception:
                pass
            return result

        elif action == "preview":
            return self._preview_organization()

        else:
            return f"Acción '{action}' no reconocida. Usa: status, organize, scan, preview"

    def get_status(self) -> str:
        """Obtener estado del bot."""
        return "Organizer operativo"

    def is_available(self) -> bool:
        """Verificar si el bot está disponible."""
        return True

    def _organize_by_type(self) -> str:
        """Organizar archivos por tipo."""
        try:
            # Directorio de descargas como ejemplo
            downloads_dir = Path.home() / "Downloads"
            if not downloads_dir.exists():
                return "❌ Directorio de descargas no encontrado"

            organized_count = 0
            created_dirs = set()

            # Escanear archivos
            for file_path in downloads_dir.iterdir():
                if file_path.is_file():
                    # Determinar categoría
                    category = self._get_file_category(file_path.suffix.lower())
                    if category:
                        # Crear directorio si no existe
                        category_dir = downloads_dir / category
                        if not category_dir.exists():
                            category_dir.mkdir()
                            created_dirs.add(category)

                        # Mover archivo
                        new_path = category_dir / file_path.name
                        if not new_path.exists():  # Evitar sobrescribir
                            shutil.move(str(file_path), str(new_path))
                            organized_count += 1

            result = f"✅ Organización completada:\n"
            result += f"• Archivos organizados: {organized_count}\n"
            if created_dirs:
                result += f"• Directorios creados: {', '.join(created_dirs)}\n"

            return result

        except Exception as e:
            return f"❌ Error organizando archivos: {str(e)}"

    def _scan_and_organize(self) -> str:
        """Escanear y organizar archivos."""
        try:
            downloads_dir = Path.home() / "Downloads"
            if not downloads_dir.exists():
                return "❌ Directorio de descargas no encontrado"

            # Contar archivos por tipo
            file_counts = {}
            total_files = 0

            for file_path in downloads_dir.iterdir():
                if file_path.is_file():
                    total_files += 1
                    category = self._get_file_category(file_path.suffix.lower())
                    if category:
                        file_counts[category] = file_counts.get(category, 0) + 1

            result = f"📊 Análisis de {downloads_dir}:\n"
            result += f"• Total archivos: {total_files}\n\n"

            if file_counts:
                result += "Archivos por categoría:\n"
                for category, count in sorted(file_counts.items()):
                    result += f"• {category}: {count} archivos\n"

                result += "\n💡 Ejecuta 'organizer organize' para organizar automáticamente"
            else:
                result += "✅ Todos los archivos ya están organizados"

            return result

        except Exception as e:
            return f"❌ Error escaneando archivos: {str(e)}"

    def _preview_organization(self) -> str:
        """Vista previa de la organización."""
        try:
            downloads_dir = Path.home() / "Downloads"
            if not downloads_dir.exists():
                return "❌ Directorio de descargas no encontrado"

            preview = "📋 Vista previa de organización:\n\n"

            for file_path in downloads_dir.iterdir():
                if file_path.is_file():
                    category = self._get_file_category(file_path.suffix.lower())
                    if category:
                        preview += f"• {file_path.name} → {category}/\n"

            if preview == "📋 Vista previa de organización:\n\n":
                preview += "✅ No hay archivos para organizar"

            return preview

        except Exception as e:
            return f"❌ Error generando vista previa: {str(e)}"

    def _get_file_category(self, extension: str) -> str:
        """Obtener categoría de un archivo por extensión."""
        for category, extensions in self.file_categories.items():
            if extension in extensions:
                return category
        return None
