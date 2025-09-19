"""Bot Indexer - Indexa y busca archivos."""

from backendbot.core.di.container import container
import os
import hashlib
from pathlib import Path


class IndexerBot:
    """Bot Indexer - Indexa y busca archivos."""

    def __init__(self) -> None:
        self.logger = container.get_logger()
        self.config = container.get_config_manager()
        self.data_repo = container.get_data_repository()
        self.index = {}  # Caché simple de archivos

    def execute(self, action: str) -> str:
        """Ejecutar acción del indexer."""
        if action == "status":
            return "🔍 Indexer listo para buscar archivos"

        elif action.startswith("search"):
            query = action.replace("search", "").strip()
            return self._search_files(query)

        elif action == "index":
            return self._build_index()

        elif action == "find_duplicates":
            return self._find_duplicates()

        else:
            return f"Acción '{action}' no reconocida. Usa: status, search [término], index, find_duplicates"

    def get_status(self) -> str:
        """Obtener estado del bot."""
        return "Indexer operativo"

    def is_available(self) -> bool:
        """Verificar si el bot está disponible."""
        return True

    def _search_files(self, query: str) -> str:
        """Buscar archivos por nombre."""
        if not query:
            return "❌ Especifica un término de búsqueda"

        try:
            results = []
            search_dirs = [Path.home() / "Documents", Path.home() / "Downloads", Path.home() / "Desktop"]

            for search_dir in search_dirs:
                if search_dir.exists():
                    for file_path in search_dir.rglob("*"):
                        if file_path.is_file() and query.lower() in file_path.name.lower():
                            size_mb = file_path.stat().st_size / 1024 / 1024
                            results.append(f"• {file_path.name} ({size_mb:.1f}MB) - {file_path.parent}")

            if results:
                result = f"🔍 Resultados para '{query}':\n" + "\n".join(results[:20])  # Máximo 20 resultados
                if len(results) > 20:
                    result += f"\n... y {len(results) - 20} más"
                return result
            else:
                return f"❌ No se encontraron archivos con '{query}'"

        except Exception as e:
            return f"❌ Error buscando archivos: {str(e)}"

    def _build_index(self) -> str:
        """Construir índice de archivos."""
        try:
            self.index = {}
            indexed_count = 0
            search_dirs = [Path.home() / "Documents", Path.home() / "Downloads"]

            for search_dir in search_dirs:
                if search_dir.exists():
                    for file_path in search_dir.rglob("*"):
                        if file_path.is_file():
                            self.index[file_path.name.lower()] = str(file_path)
                            indexed_count += 1

            return f"✅ Índice construido: {indexed_count} archivos indexados"

        except Exception as e:
            return f"❌ Error construyendo índice: {str(e)}"

    def _find_duplicates(self) -> str:
        """Buscar archivos duplicados."""
        try:
            file_hashes = {}
            duplicates = []

            search_dirs = [Path.home() / "Documents", Path.home() / "Downloads", Path.home() / "Desktop"]

            # Calcular hashes
            for search_dir in search_dirs:
                if search_dir.exists():
                    for file_path in search_dir.rglob("*"):
                        if file_path.is_file() and file_path.stat().st_size > 0:  # Solo archivos no vacíos
                            try:
                                file_hash = self._get_file_hash(file_path)
                                if file_hash in file_hashes:
                                    duplicates.append((str(file_path), file_hashes[file_hash]))
                                else:
                                    file_hashes[file_hash] = str(file_path)
                            except (OSError, IOError):
                                continue  # Saltar archivos que no se pueden leer

            if duplicates:
                result = "🔍 Archivos duplicados encontrados:\n"
                for dup1, dup2 in duplicates[:10]:  # Máximo 10 duplicados
                    result += f"• {Path(dup1).name}\n  ↳ {dup1}\n  ↳ {dup2}\n\n"
                if len(duplicates) > 10:
                    result += f"... y {len(duplicates) - 10} pares más"
                return result
            else:
                return "✅ No se encontraron archivos duplicados"

        except Exception as e:
            return f"❌ Error buscando duplicados: {str(e)}"

    def _get_file_hash(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Calcular hash MD5 de un archivo."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
