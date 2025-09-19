"""
Tests for Indexer Worker
========================

Tests unitarios completos para IndexerWorker siguiendo TDD.
Cubre indexación, búsqueda, filtros, persistencia y threading.

Autor: BackendBot Team
Versión: 0.1.0
"""

import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from backendbot.packages.bots.base_bot import BotState
from backendbot.packages.bots.indexer_worker import FileIndex, IndexerWorker


@pytest.fixture
def indexer_worker():
    """Fixture para crear un IndexerWorker de prueba."""
    worker = IndexerWorker(bot_id="test-indexer", name="Test Indexer")

    # Configuración de prueba
    worker.config.update(
        {
            "index_paths": ["."],
            "exclude_patterns": [r"\.git/", r"__pycache__/"],
            "include_patterns": [r".*"],
            "index_file_types": {".txt", ".py", ".md"},
            "max_file_size_mb": 10,
            "index_content": True,
            "index_metadata": True,
            "persistent_index": False,  # Deshabilitar para tests
            "execution_interval": 60,
        }
    )
    worker.on_config_updated()  # Aplicar configuración

    return worker


@pytest.fixture
def temp_dir():
    """Fixture para crear directorio temporal."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestIndexerWorker:
    """Tests para IndexerWorker."""

    def test_initialization(self, indexer_worker):
        """Test inicialización del IndexerWorker."""
        assert indexer_worker.bot_id == "test-indexer"
        assert indexer_worker.name == "Test Indexer"
        assert indexer_worker.index_paths == ["."]
        assert len(indexer_worker.exclude_patterns) > 0
        assert len(indexer_worker.include_patterns) > 0
        assert ".txt" in indexer_worker.index_file_types
        assert indexer_worker.max_file_size_mb == 10
        assert indexer_worker.index_content is True
        assert indexer_worker.index_metadata is True

    def test_config_validation_valid(self, indexer_worker):
        """Test validación de configuración válida."""
        valid_config = {
            "index_paths": ["/tmp", "/home"],
            "exclude_patterns": [r"\.git/"],
            "include_patterns": [r".*"],
            "index_file_types": {".txt", ".py"},
            "max_file_size_mb": 50,
        }
        assert indexer_worker.validate_config(valid_config)

    def test_config_validation_invalid_missing_keys(self, indexer_worker):
        """Test validación de configuración con claves faltantes."""
        invalid_config = {
            "exclude_patterns": [r"\.git/"]
            # Falta index_paths
        }
        assert not indexer_worker.validate_config(invalid_config)

    def test_config_validation_invalid_types(self, indexer_worker):
        """Test validación de configuración con tipos inválidos."""
        invalid_config = {
            "index_paths": "/tmp",  # Debe ser lista
            "exclude_patterns": r"\.git/",  # Debe ser lista
            "include_patterns": [r".*"],
        }
        assert not indexer_worker.validate_config(invalid_config)

    def test_should_run_in_background(self, indexer_worker):
        """Test que debe ejecutarse en background."""
        assert indexer_worker.should_run_in_background() is True

    def test_get_execution_interval(self, indexer_worker):
        """Test obtener intervalo de ejecución."""
        assert indexer_worker.get_execution_interval() == 60

    def test_should_index_file_size_filter(self, indexer_worker, temp_dir):
        """Test filtro de archivos por tamaño."""
        # Archivo pequeño (válido)
        small_file = temp_dir / "small.txt"
        small_file.write_text("small content")
        assert indexer_worker._should_index_file(small_file)

        # Archivo grande (inválido)
        large_content = "x" * (11 * 1024 * 1024)  # 11MB
        large_file = temp_dir / "large.txt"
        large_file.write_text(large_content)
        assert not indexer_worker._should_index_file(large_file)

    def test_should_index_file_exclude_patterns(self, indexer_worker, temp_dir):
        """Test filtro de archivos por patrones de exclusión."""
        # Archivo normal (válido)
        normal_file = temp_dir / "normal.txt"
        normal_file.write_text("content")
        assert indexer_worker._should_index_file(normal_file)

        # Archivo en directorio excluido (inválido)
        git_file = temp_dir / ".git" / "config"
        git_file.parent.mkdir()
        git_file.write_text("git config")
        assert not indexer_worker._should_index_file(git_file)

    def test_should_index_file_include_patterns(self, indexer_worker, temp_dir):
        """Test filtro de archivos por patrones de inclusión."""
        # Archivo que coincide con patrón (válido)
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("content")
        assert indexer_worker._should_index_file(txt_file)

        # Archivo que no coincide (inválido si hay patrones restrictivos)
        # Nota: El patrón por defecto .* incluye todo

    def test_should_index_file_type_filter(self, indexer_worker, temp_dir):
        """Test filtro de archivos por tipo."""
        # Archivo de tipo indexado (válido)
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("content")
        assert indexer_worker._should_index_file(txt_file)

        # Archivo de tipo no indexado (inválido)
        bin_file = temp_dir / "test.bin"
        bin_file.write_bytes(b"binary content")
        assert not indexer_worker._should_index_file(bin_file)

    def test_file_needs_update_new_file(self, indexer_worker, temp_dir):
        """Test que archivo nuevo necesita actualización."""
        new_file = temp_dir / "new.txt"
        new_file.write_text("content")
        assert indexer_worker._file_needs_update(new_file)

    def test_file_needs_update_size_changed(self, indexer_worker, temp_dir):
        """Test que archivo con tamaño cambiado necesita actualización."""
        file_path = temp_dir / "test.txt"
        file_path.write_text("content")

        # Indexar archivo
        indexer_worker._index_file(file_path)

        # Cambiar tamaño
        file_path.write_text("much longer content that changes the file size")

        assert indexer_worker._file_needs_update(file_path)

    def test_index_file_success(self, indexer_worker, temp_dir):
        """Test indexación exitosa de archivo."""
        txt_file = temp_dir / "test.txt"
        content = "This is a test file with some content for indexing."
        txt_file.write_text(content)

        result = indexer_worker._index_file(txt_file)

        assert result is True
        assert str(txt_file) in indexer_worker.file_index

        file_index = indexer_worker.file_index[str(txt_file)]
        assert file_index.name == "test.txt"
        assert file_index.extension == ".txt"
        assert file_index.size == len(content.encode())
        assert file_index.line_count == 1
        assert file_index.word_count == 10  # Ajustado al conteo real
        assert not file_index.is_binary
        assert "document" in file_index.tags

    def test_index_file_binary(self, indexer_worker, temp_dir):
        """Test indexación de archivo binario."""
        bin_file = temp_dir / "test.jpg"
        bin_file.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01")  # JPEG header

        result = indexer_worker._index_file(bin_file)

        assert result is True
        assert str(bin_file) in indexer_worker.file_index

        file_index = indexer_worker.file_index[str(bin_file)]
        assert file_index.is_binary is True
        assert "image" in file_index.tags

    def test_calculate_file_hash(self, indexer_worker, temp_dir):
        """Test cálculo de hash de archivo."""
        file_path = temp_dir / "test.txt"
        content = "test content"
        file_path.write_text(content)

        hash1 = indexer_worker._calculate_file_hash(file_path)
        hash2 = indexer_worker._calculate_file_hash(file_path)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length

    def test_detect_file_type(self, indexer_worker, temp_dir):
        """Test detección de tipo de archivo."""
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("content")

        mime_type, encoding = indexer_worker._detect_file_type(txt_file)

        assert mime_type == "text/plain"
        assert encoding is None

    def test_is_binary_file(self, indexer_worker, temp_dir):
        """Test detección de archivos binarios."""
        # Archivo de texto
        txt_file = temp_dir / "text.txt"
        txt_file.write_text("text content")
        assert not indexer_worker._is_binary_file(txt_file)

        # Archivo binario
        bin_file = temp_dir / "binary.bin"
        bin_file.write_bytes(b"\x00\x01\x02\x03\x00\x00\x00")
        assert indexer_worker._is_binary_file(bin_file)

    def test_extract_search_terms(self, indexer_worker):
        """Test extracción de términos de búsqueda."""
        content = "The quick brown fox jumps over the lazy dog. This is a test."
        terms = indexer_worker._extract_search_terms(content)

        assert "quick" in terms
        assert "brown" in terms
        assert "fox" in terms
        assert "jumps" in terms
        assert "lazy" in terms
        assert "dog" in terms
        assert "test" in terms

        # Palabras comunes deben estar filtradas
        assert "the" not in terms
        assert "is" not in terms
        assert "a" not in terms

        # Palabras cortas deben estar filtradas
        assert "a" not in terms
        assert "is" not in terms

    def test_execute_task_success(self, indexer_worker, temp_dir):
        """Test ejecución exitosa de tarea."""
        # Crear archivo de prueba
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("test content")

        # Cambiar configuración para usar el directorio temporal
        indexer_worker.config["index_paths"] = [str(temp_dir)]
        indexer_worker.on_config_updated()

        result = indexer_worker.execute_task()

        assert result["success"] is True
        assert "result" in result
        assert result["result"]["files_processed"] >= 1
        assert result["result"]["organization_summary"]["files_indexed"] >= 1

    def test_execute_task_error_handling(self, indexer_worker):
        """Test manejo de errores en ejecución de tarea."""
        # Configurar ruta inexistente
        indexer_worker.config["index_paths"] = ["/nonexistent/path"]
        indexer_worker.on_config_updated()

        result = indexer_worker.execute_task()

        assert (
            result["success"] is True
        )  # No falla completamente por errores en archivos
        assert "result" in result

    def test_search_files_basic(self, indexer_worker, temp_dir):
        """Test búsqueda básica de archivos."""
        # Crear y indexar archivos
        file1 = temp_dir / "doc1.txt"
        file1.write_text("This is a document about Python programming.")

        file2 = temp_dir / "doc2.txt"
        file2.write_text("JavaScript is also a programming language.")

        # Indexar archivos
        indexer_worker.config["index_paths"] = [str(temp_dir)]
        indexer_worker.on_config_updated()
        indexer_worker.execute_task()

        # Buscar
        results = indexer_worker.search_files("Python")

        assert len(results) >= 1
        assert results[0].file_index.name == "doc1.txt"
        assert "python" in results[0].matched_terms

    def test_search_files_no_results(self, indexer_worker, temp_dir):
        """Test búsqueda sin resultados."""
        # Crear archivo
        file1 = temp_dir / "test.txt"
        file1.write_text("content")

        # Indexar
        indexer_worker.config["index_paths"] = [str(temp_dir)]
        indexer_worker.on_config_updated()
        indexer_worker.execute_task()

        # Buscar término inexistente
        results = indexer_worker.search_files("nonexistent")

        assert len(results) == 0

    def test_search_files_with_filters(self, indexer_worker, temp_dir):
        """Test búsqueda con filtros."""
        # Crear archivos de diferentes tipos
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("Python programming content")

        py_file = temp_dir / "script.py"
        py_file.write_text("Python script content")

        # Indexar
        indexer_worker.config["index_paths"] = [str(temp_dir)]
        indexer_worker.on_config_updated()
        indexer_worker.execute_task()

        # Buscar con filtro de extensión
        results = indexer_worker.search_files("Python", extension=".py")

        assert len(results) >= 1
        for result in results:
            assert result.file_index.extension == ".py"

    def test_calculate_relevance_score(self, indexer_worker, temp_dir):
        """Test cálculo de puntuación de relevancia."""
        # Crear archivo
        file_path = temp_dir / "test.txt"
        file_path.write_text("Python programming is great")

        # Indexar
        indexer_worker._index_file(file_path)

        # Calcular relevancia
        query_terms = ["python", "programming"]
        score = indexer_worker._calculate_relevance_score(
            indexer_worker.file_index[str(file_path)], query_terms
        )

        assert score > 0
        assert score <= 1

    def test_get_search_context(self, indexer_worker, temp_dir):
        """Test obtención de contexto de búsqueda."""
        # Crear archivo
        file_path = temp_dir / "test.txt"
        content = (
            "This is a long text about Python programming that should provide context."
        )
        file_path.write_text(content)

        # Indexar
        indexer_worker._index_file(file_path)

        # Obtener contexto
        context = indexer_worker._get_search_context(str(file_path), ["python"])

        assert context is not None
        assert "Python" in context or "python" in context

    def test_add_remove_index_callback(self, indexer_worker):
        """Test agregar y remover callbacks de indexación."""
        callback = Mock()

        # Agregar callback
        indexer_worker.add_index_callback(callback)
        assert callback in indexer_worker.index_callbacks

        # Remover callback
        indexer_worker.remove_index_callback(callback)
        assert callback not in indexer_worker.index_callbacks

    def test_get_index_stats(self, indexer_worker, temp_dir):
        """Test obtener estadísticas del índice."""
        # Crear e indexar archivo
        file_path = temp_dir / "test.txt"
        file_path.write_text("content")

        indexer_worker.config["index_paths"] = [str(temp_dir)]
        indexer_worker.on_config_updated()
        indexer_worker.execute_task()

        stats = indexer_worker.get_index_stats()

        assert "total_files" in stats
        assert "total_size_mb" in stats
        assert "file_types" in stats
        assert "largest_files" in stats
        assert stats["total_files"] >= 1

    def test_clear_index(self, indexer_worker, temp_dir):
        """Test limpiar índice."""
        # Crear e indexar archivo
        file_path = temp_dir / "test.txt"
        file_path.write_text("content")

        indexer_worker.config["index_paths"] = [str(temp_dir)]
        indexer_worker.on_config_updated()
        indexer_worker.execute_task()

        # Verificar que hay archivos indexados
        assert len(indexer_worker.file_index) >= 1

        # Limpiar índice
        indexer_worker.clear_index()

        # Verificar que está vacío
        assert len(indexer_worker.file_index) == 0
        assert len(indexer_worker.search_index) == 0
        assert len(indexer_worker.reverse_index) == 0

    def test_threading_execution(self, indexer_worker, temp_dir):
        """Test ejecución con threading."""
        # Crear archivo de prueba
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("test content")

        # Cambiar configuración
        indexer_worker.config["index_paths"] = [str(temp_dir)]
        indexer_worker.on_config_updated()

        # Iniciar worker
        indexer_worker.start()

        # Ejecutar tarea manualmente
        result = indexer_worker.execute_task()

        # Verificar estado
        assert indexer_worker.state == BotState.RUNNING
        assert result["success"] is True

        # Detener worker
        indexer_worker.stop()

        import time

        time.sleep(1)
        assert indexer_worker.state == BotState.STOPPED

    def test_repr(self, indexer_worker):
        """Test representación string del worker."""
        repr_str = repr(indexer_worker)
        assert "IndexerWorker" in repr_str
        assert "test-indexer" in repr_str
        assert "files=" in repr_str

    def test_file_index_serialization(self, temp_dir):
        """Test serialización de FileIndex."""
        file_index = FileIndex(
            path=str(temp_dir / "test.txt"),
            name="test.txt",
            extension=".txt",
            size=100,
            modified_time=datetime.now(),
            created_time=datetime.now(),
            content_hash="hash123",
            mime_type="text/plain",
        )

        # Serializar
        data = file_index.to_dict()

        # Deserializar
        restored = FileIndex.from_dict(data)

        assert restored.path == file_index.path
        assert restored.name == file_index.name
        assert restored.extension == file_index.extension
        assert restored.size == file_index.size
        assert restored.mime_type == file_index.mime_type

    # Test eliminado: SearchResult ya no está definido
