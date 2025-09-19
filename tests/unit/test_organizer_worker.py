"""
Tests para Organizer Worker
===========================

Tests unitarios siguiendo metodología TDD para OrganizerWorker.
Pruebas de funcionalidad de organización, movimiento y eliminación de archivos.

Autor: BackendBot Team
Versión: 0.1.0
"""

import os
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from backendbot.packages.bots.base_bot import BotState
from backendbot.packages.bots.organizer_worker import OrganizerWorker
from backendbot.packages.models.models import FileOrganizationResult


class TestOrganizerWorker:
    """Tests para OrganizerWorker."""

    @pytest.fixture
    def temp_dir(self):
        """Fixture para directorio temporal."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        # Cleanup
        shutil.rmtree(temp_path, ignore_errors=True)

    @pytest.fixture
    def organizer_worker(self, temp_dir):
        """Fixture para crear instancia de OrganizerWorker."""
        # Configurar para usar directorio temporal
        config = {
            "scan_paths": [str(temp_dir)],
            "dry_run": True,  # Modo simulación por defecto
            "organization_rules": {
                "by_type": True,
                "min_file_size_mb": 0,  # Procesar todos los archivos
                "max_file_age_days": 365,  # Procesar archivos antiguos
                "auto_delete_temp": True,
            },
        }

        worker = OrganizerWorker(bot_id="test-organizer", name="Test Organizer")
        worker.config.update(config)
        yield worker
        # Cleanup
        if worker.state == BotState.RUNNING:
            worker.stop()

    def test_initialization(self, organizer_worker):
        """Test inicialización correcta del OrganizerWorker."""
        assert organizer_worker.bot_id == "test-organizer"
        assert organizer_worker.name == "Test Organizer"
        assert len(organizer_worker.scan_paths) > 0
        assert organizer_worker.organization_rules["by_type"] is True
        assert organizer_worker.last_scan_result is None
        assert len(organizer_worker.organization_history) == 0

    def test_config_validation_valid(self, organizer_worker):
        """Test validación de configuración válida."""
        valid_config = {
            "scan_paths": ["/tmp/test"],
            "organization_rules": {"by_type": True, "min_file_size_mb": 1},
        }
        assert organizer_worker.validate_config(valid_config)

    def test_config_validation_invalid_missing_keys(self, organizer_worker):
        """Test validación de configuración con claves faltantes."""
        invalid_config = {"scan_paths": ["/tmp"]}  # Falta organization_rules
        assert not organizer_worker.validate_config(invalid_config)

    def test_config_validation_invalid_scan_paths(self, organizer_worker):
        """Test validación de configuración con scan_paths inválido."""
        invalid_config = {
            "scan_paths": "/tmp",  # Debe ser lista
            "organization_rules": {"by_type": True},
        }
        assert not organizer_worker.validate_config(invalid_config)

    def test_should_run_in_background(self, organizer_worker):
        """Test que el worker debe ejecutarse en background."""
        assert organizer_worker.should_run_in_background() is True

    def test_get_execution_interval(self, organizer_worker):
        """Test obtener intervalo de ejecución."""
        assert organizer_worker.get_execution_interval() == 3600  # 1 hora por defecto

    def test_should_process_file_size_filter(self, organizer_worker, temp_dir):
        """Test filtro de archivos por tamaño."""
        # Crear archivo pequeño (menos de 1MB)
        small_file = temp_dir / "small.txt"
        small_file.write_text("small content")

        # Configurar filtro de tamaño mínimo
        organizer_worker.organization_rules["min_file_size_mb"] = 1

        assert not organizer_worker._should_process_file(small_file)

        # Crear archivo grande
        large_file = temp_dir / "large.txt"
        large_content = "x" * (2 * 1024 * 1024)  # 2MB
        large_file.write_text(large_content)

        assert organizer_worker._should_process_file(large_file)

    def test_should_process_file_age_filter(self, organizer_worker, temp_dir):
        """Test filtro de archivos por edad."""
        # Crear archivo reciente con contenido suficiente
        recent_file = temp_dir / "recent.txt"
        # Crear contenido de al menos 1MB
        content = "x" * (1024 * 1024 + 100)  # 1MB + 100 bytes
        recent_file.write_text(content)

        # Configurar filtro de edad máxima (archivos más nuevos que este límite)
        organizer_worker.organization_rules["max_file_age_days"] = 30

        assert organizer_worker._should_process_file(recent_file)

        # Simular archivo antiguo modificando timestamp
        old_timestamp = (datetime.now() - timedelta(days=60)).timestamp()
        os.utime(str(recent_file), (old_timestamp, old_timestamp))

        assert not organizer_worker._should_process_file(recent_file)

    def test_should_process_file_ignore_dirs(self, organizer_worker, temp_dir):
        """Test ignorar directorios de sistema."""
        # Crear archivos en directorios ignorados
        git_file = temp_dir / ".git" / "config"
        git_file.parent.mkdir()
        git_file.write_text("git config")

        pycache_file = temp_dir / "__pycache__" / "module.pyc"
        pycache_file.parent.mkdir()
        pycache_file.write_bytes(b"bytecode")

        assert not organizer_worker._should_process_file(git_file)
        assert not organizer_worker._should_process_file(pycache_file)

    def test_organize_by_type_documents(self, organizer_worker, temp_dir):
        """Test organización por tipo - documentos."""
        # Crear archivo PDF
        pdf_file = temp_dir / "document.pdf"
        pdf_file.write_text("pdf content")

        new_path = organizer_worker._organize_by_type(pdf_file)

        assert new_path is not None
        assert "documents" in str(new_path)
        assert new_path.name == "document.pdf"

    def test_organize_by_type_images(self, organizer_worker, temp_dir):
        """Test organización por tipo - imágenes."""
        # Crear archivo JPG
        jpg_file = temp_dir / "photo.jpg"
        jpg_file.write_text("jpg content")

        new_path = organizer_worker._organize_by_type(jpg_file)

        assert new_path is not None
        assert "images" in str(new_path)
        assert new_path.name == "photo.jpg"

    def test_organize_by_type_unknown(self, organizer_worker, temp_dir):
        """Test organización por tipo - tipo desconocido."""
        # Crear archivo con extensión desconocida
        unknown_file = temp_dir / "file.unknown"
        unknown_file.write_text("unknown content")

        new_path = organizer_worker._organize_by_type(unknown_file)

        assert new_path is not None
        assert "others" in str(new_path)
        assert new_path.name == "file.unknown"

    def test_organize_by_type_name_collision(self, organizer_worker, temp_dir):
        """Test organización por tipo - colisión de nombres."""
        # Crear dos archivos con el mismo nombre
        file1 = temp_dir / "documents" / "test.pdf"
        file1.parent.mkdir()
        file1.write_text("content 1")

        file2 = temp_dir / "test.pdf"
        file2.write_text("content 2")

        # Simular que el directorio documents ya existe con archivo
        organizer_worker.config["dry_run"] = False
        new_path = organizer_worker._organize_by_type(file2)

        assert new_path is not None
        assert new_path.name.startswith("test_")
        assert new_path.name.endswith(".pdf")

    def test_should_delete_file_temp_extensions(self, organizer_worker, temp_dir):
        """Test eliminación de archivos temporales por extensión."""
        # Crear archivo temporal
        temp_file = temp_dir / "temp.tmp"
        temp_file.write_text("temp content")

        assert organizer_worker._should_delete_file(temp_file)

    def test_should_delete_file_temp_prefix(self, organizer_worker, temp_dir):
        """Test eliminación de archivos temporales por prefijo."""
        # Crear archivo con prefijo ~
        temp_file = temp_dir / "~temp.txt"
        temp_file.write_text("temp content")

        assert organizer_worker._should_delete_file(temp_file)

    def test_should_delete_file_normal_file(self, organizer_worker, temp_dir):
        """Test no eliminar archivos normales."""
        # Crear archivo normal
        normal_file = temp_dir / "normal.txt"
        normal_file.write_text("normal content")

        assert not organizer_worker._should_delete_file(normal_file)

    @patch("backendbot.packages.bots.organizer_worker.shutil.move")
    def test_move_file_success(self, mock_move, organizer_worker, temp_dir):
        """Test movimiento exitoso de archivo."""
        source = temp_dir / "source.txt"
        source.write_text("content")
        destination = temp_dir / "dest.txt"

        # Desactivar dry run
        organizer_worker.config["dry_run"] = False

        result = organizer_worker._move_file(source, destination)

        assert result is True
        mock_move.assert_called_once_with(str(source), str(destination))

    @patch("backendbot.packages.bots.organizer_worker.shutil.move")
    def test_move_file_dry_run(self, mock_move, organizer_worker, temp_dir):
        """Test movimiento en modo dry run."""
        source = temp_dir / "source.txt"
        destination = temp_dir / "dest.txt"

        # Activar dry run
        organizer_worker.config["dry_run"] = True

        result = organizer_worker._move_file(source, destination)

        assert result is True
        mock_move.assert_not_called()

    @patch("backendbot.packages.bots.organizer_worker.shutil.move")
    def test_move_file_error(self, mock_move, organizer_worker, temp_dir):
        """Test error en movimiento de archivo."""
        source = temp_dir / "source.txt"
        destination = temp_dir / "dest.txt"

        # Configurar mock para lanzar excepción
        mock_move.side_effect = Exception("Move failed")

        # Desactivar dry run
        organizer_worker.config["dry_run"] = False

        result = organizer_worker._move_file(source, destination)

        assert result is False

    @patch("backendbot.packages.bots.organizer_worker.Path.unlink")
    def test_delete_file_success(self, mock_unlink, organizer_worker, temp_dir):
        """Test eliminación exitosa de archivo."""
        file_path = temp_dir / "to_delete.txt"

        # Desactivar dry run
        organizer_worker.config["dry_run"] = False

        result = organizer_worker._delete_file(file_path)

        assert result is True
        mock_unlink.assert_called_once()

    def test_delete_file_dry_run(self, organizer_worker, temp_dir):
        """Test eliminación en modo dry run."""
        file_path = temp_dir / "to_delete.txt"

        # Activar dry run
        organizer_worker.config["dry_run"] = True

        result = organizer_worker._delete_file(file_path)

        assert result is True

    @patch("backendbot.packages.bots.organizer_worker.shutil.copy2")
    def test_create_backup(self, mock_copy, organizer_worker, temp_dir):
        """Test creación de backup."""
        file_path = temp_dir / "original.txt"
        file_path.write_text("content")

        organizer_worker._create_backup(file_path)

        # Verificar que se llamó a copy2
        assert mock_copy.called
        call_args = mock_copy.call_args[0]
        assert str(file_path) == call_args[0]
        assert "backups" in call_args[1]
        assert ".bak" in call_args[1]

    def test_execute_task_success(self, organizer_worker, temp_dir):
        """Test ejecución exitosa de tarea."""
        # Crear algunos archivos de prueba
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("test content")

        pdf_file = temp_dir / "document.pdf"
        pdf_file.write_text("pdf content")

        result = organizer_worker.execute_task()

        assert result["success"] is True
        assert "result" in result
        assert "timestamp" in result
        assert result["result"]["files_processed"] >= 2

    def test_execute_task_error_handling(self, organizer_worker):
        """Test manejo de errores en ejecución de tarea."""
        # Configurar scan_paths con directorio inexistente
        organizer_worker.scan_paths = ["/nonexistent/path"]

        result = organizer_worker.execute_task()

        assert result["success"] is True  # No falla completamente por un error
        assert "result" in result
        assert result["result"]["errors_count"] > 0

    def test_organization_callbacks(self, organizer_worker, temp_dir):
        """Test sistema de callbacks para organización."""
        callback_mock = Mock()

        organizer_worker.add_organization_callback(callback_mock)

        # Crear archivo y ejecutar organización
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("content")

        organizer_worker.execute_task()

        # Verificar que el callback fue llamado
        callback_mock.assert_called_once()
        call_args = callback_mock.call_args[0][0]
        assert isinstance(call_args, FileOrganizationResult)

    def test_remove_organization_callback(self, organizer_worker, temp_dir):
        """Test remover callback de organización."""
        callback_mock = Mock()
        organizer_worker.add_organization_callback(callback_mock)
        organizer_worker.remove_organization_callback(callback_mock)

        # Crear archivo y ejecutar organización
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("content")

        organizer_worker.execute_task()

        # Verificar que el callback NO fue llamado
        callback_mock.assert_not_called()

    def test_get_last_scan_result_none(self, organizer_worker):
        """Test obtener último resultado cuando no hay."""
        assert organizer_worker.get_last_scan_result() is None

    def test_get_last_scan_result(self, organizer_worker, temp_dir):
        """Test obtener último resultado de escaneo."""
        # Crear archivo y ejecutar organización
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("content")

        organizer_worker.execute_task()
        result = organizer_worker.get_last_scan_result()

        assert result is not None
        assert "files_processed" in result
        assert "files_moved" in result
        assert "errors_count" in result

    def test_get_organization_history_empty(self, organizer_worker):
        """Test obtener historial vacío."""
        history = organizer_worker.get_organization_history()
        assert len(history) == 0

    def test_get_organization_history(self, organizer_worker, temp_dir):
        """Test obtener historial de organización."""
        # Ejecutar múltiples organizaciones
        for i in range(3):
            txt_file = temp_dir / f"test{i}.txt"
            txt_file.write_text(f"content {i}")
            organizer_worker.execute_task()

        history = organizer_worker.get_organization_history(limit=2)
        assert len(history) == 2

    def test_get_statistics(self, organizer_worker):
        """Test obtener estadísticas."""
        stats = organizer_worker.get_statistics()

        assert "total_files_processed" in stats
        assert "total_files_moved" in stats
        assert "total_files_deleted" in stats
        assert "total_errors" in stats
        assert "success_rate" in stats

        # Verificar valores iniciales
        assert stats["total_files_processed"] == 0
        assert stats["total_files_moved"] == 0
        assert stats["total_files_deleted"] == 0
        assert stats["total_errors"] == 0

    def test_threading_execution(self, organizer_worker, temp_dir):
        """Test ejecución con threading."""
        # Crear archivo de prueba
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("test content")

        # Iniciar worker
        organizer_worker.start()

        # Ejecutar tarea manualmente (ya que el intervalo es de 1 hora)
        organizer_worker.execute_task()

        # Verificar que está ejecutando
        assert organizer_worker.state == BotState.RUNNING
        assert organizer_worker.get_last_scan_result() is not None

        # Detener worker
        organizer_worker.stop()

        # Esperar a que termine
        import time

        time.sleep(1)
        assert organizer_worker.state == BotState.STOPPED

    def test_repr(self, organizer_worker):
        """Test representación string del worker."""
        repr_str = repr(organizer_worker)
        assert "OrganizerWorker" in repr_str
        assert "test-organizer" in repr_str
        assert "processed=0" in repr_str
        assert "moved=0" in repr_str
        assert "errors=0" in repr_str
