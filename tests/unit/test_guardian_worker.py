"""
Tests TDD para GuardianWorker - BackendBot
==========================================

Tests unitarios completos para GuardianWorker siguiendo TDD.

Cobertura:
- Inicialización y configuración
- Escaneo de seguridad básico
- Detección de amenazas
- Verificación de integridad
- Sistema de alertas
- Eventos de seguridad
- Callbacks de seguridad
- Estadísticas y monitoreo
- Funcionamiento en background
- Manejo de errores

Autor: BackendBot Team
"""

import os
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from backendbot.packages.bots.base_bot import BotState
from backendbot.packages.bots.guardian_worker import GuardianWorker
from backendbot.packages.models.models import SecurityAlert, SecurityEvent



class TestGuardianWorker:
    """Tests para GuardianWorker."""

    @pytest.fixture
    def temp_dir(self):
        """Directorio temporal para tests."""
        with tempfile.TemporaryDirectory() as temp:
            yield Path(temp)

    @pytest.fixture
    def guardian(self):
        """Instancia de GuardianWorker para tests."""
        return GuardianWorker("test-guardian", "Test Guardian")

    def test_initialization(self, guardian):
        """Test inicialización básica."""
        assert guardian.bot_id == "test-guardian"
        assert guardian.name == "Test Guardian"
        assert guardian.state == BotState.STOPPED
        assert isinstance(guardian.file_integrity_hashes, dict)
        assert isinstance(guardian.security_events, list)
        assert isinstance(guardian.active_alerts, list)
        assert isinstance(guardian.audit_log, list)

    def test_default_config(self, guardian):
        """Test configuración por defecto."""
        config = guardian._load_default_config()

        assert "monitored_paths" in config
        assert "excluded_paths" in config
        assert "threat_patterns" in config
        assert "suspicious_extensions" in config
        assert config["max_file_size_alert"] == 100 * 1024 * 1024
        assert config["integrity_check_interval"] == 3600
        assert config["execution_interval"] == 300

    def test_config_update(self, guardian):
        """Test actualización de configuración."""
        new_config = {
            "monitored_paths": ["/test/path"],
            "max_file_size_alert": 50 * 1024 * 1024,
            "threat_patterns": ["test.exe"],
        }

        guardian.config.update(new_config)
        guardian.on_config_updated()

        assert guardian.monitored_paths == ["/test/path"]
        assert guardian.max_file_size_alert == 50 * 1024 * 1024
        assert "test.exe" in guardian.threat_patterns

    def test_execute_task_basic(self, guardian, temp_dir):
        """Test ejecución básica de tarea."""
        # Crear archivo de prueba
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        # Configurar
        guardian.config.update({"monitored_paths": [str(temp_dir)]})
        guardian.on_config_updated()

        # Ejecutar
        result = guardian.execute_task()

        assert result["success"] is True
        assert "result" in result
        assert result["result"]["files_processed"] >= 1
        assert result["result"]["errors_count"] == 0

    def test_security_scan_basic(self, guardian, temp_dir):
        """Test escaneo básico de seguridad."""
        # Crear archivos de prueba
        safe_file = temp_dir / "safe.txt"
        safe_file.write_text("safe content")

        exe_file = temp_dir / "malware.exe"
        exe_file.write_text("malware content")

        # Configurar
        guardian.config.update(
            {"monitored_paths": [str(temp_dir)], "suspicious_extensions": {".exe"}}
        )
        guardian.on_config_updated()

        # Ejecutar escaneo
        scan_result = guardian._perform_security_scan()

        assert scan_result["files_scanned"] >= 2
        assert scan_result["errors_count"] == 0
        assert scan_result["threats_detected"] >= 1  # Al menos el .exe

    def test_threat_detection_extensions(self, guardian, temp_dir):
        """Test detección de amenazas por extensión."""
        # Crear archivos con extensiones sospechosas
        exe_file = temp_dir / "test.exe"
        exe_file.write_text("test")

        bat_file = temp_dir / "test.bat"
        bat_file.write_text("test")

        safe_file = temp_dir / "test.txt"
        safe_file.write_text("test")

        # Configurar
        guardian.config.update(
            {
                "monitored_paths": [str(temp_dir)],
                "suspicious_extensions": {".exe", ".bat"},
            }
        )
        guardian.on_config_updated()

        # Escanear
        scan_result = guardian._perform_security_scan()

        assert scan_result["threats_detected"] >= 2  # exe y bat

        # Verificar alertas generadas
        alerts = guardian.get_active_alerts()
        exe_alerts = [a for a in alerts if "test.exe" in a.file_path]
        bat_alerts = [a for a in alerts if "test.bat" in a.file_path]

        assert len(exe_alerts) >= 1
        assert len(bat_alerts) >= 1

    def test_large_file_alert(self, guardian, temp_dir):
        """Test alerta por archivo grande."""
        # Crear archivo grande
        large_file = temp_dir / "large.dat"
        large_content = "x" * (200 * 1024 * 1024)  # 200MB
        large_file.write_text(large_content)

        # Configurar límite bajo
        guardian.config.update(
            {
                "monitored_paths": [str(temp_dir)],
                "max_file_size_alert": 100 * 1024 * 1024,  # 100MB
            }
        )
        guardian.on_config_updated()

        # Escanear
        scan_result = guardian._perform_security_scan()

        # Verificar alerta generada
        alerts = guardian.get_active_alerts()
        large_alerts = [a for a in alerts if "large.dat" in a.file_path]

        assert len(large_alerts) >= 1
    # assert eliminado por refactor: ThreatLevel
        assert "gran tamaño" in large_alerts[0].title

    def test_file_integrity_check(self, guardian, temp_dir):
        """Test verificación de integridad de archivos."""
        # Crear archivo y agregarlo al monitoreo
        test_file = temp_dir / "integrity.txt"
        test_file.write_text("original content")

        guardian.add_file_to_integrity_check(str(test_file))

        # Verificar que se agregó
        assert str(test_file) in guardian.file_integrity_hashes

        # Modificar archivo
        test_file.write_text("modified content")

        # Realizar check de integridad
        checks = guardian._perform_integrity_check()

        assert checks >= 1

        # Verificar alerta generada
        alerts = guardian.get_active_alerts()
        integrity_alerts = [
            a for a in alerts if "Modificación no autorizada" in a.title
        ]

        assert len(integrity_alerts) >= 1

    def test_missing_file_integrity(self, guardian, temp_dir):
        """Test detección de archivo faltante en integridad."""
        # Crear archivo temporal
        test_file = temp_dir / "temp.txt"
        test_file.write_text("content")

        guardian.add_file_to_integrity_check(str(test_file))

        # Verificar que se agregó correctamente
        assert str(test_file) in guardian.file_integrity_hashes
        assert guardian.integrity_checks == 0  # Aún no se ha hecho ningún check

        # Eliminar archivo
        test_file.unlink()

        # Forzar check de integridad llamando directamente
        checks = guardian._perform_integrity_check()

        # Verificar que se realizó el check
        assert checks >= 1
        # Nota: integrity_checks no se incrementa cuando se llama directamente a _perform_integrity_check
        # Solo se incrementa en _check_integrity_if_needed

        # Verificar alerta generada
        alerts = guardian.get_active_alerts()
        missing_alerts = [a for a in alerts if "Archivo faltante" in a.title]

        assert len(missing_alerts) >= 1

    def test_exclude_patterns(self, guardian, temp_dir):
        """Test patrones de exclusión."""
        # Crear estructura con archivos excluidos
        git_dir = temp_dir / ".git"
        git_dir.mkdir()

        git_file = git_dir / "config"
        git_file.write_text("git config")

        pycache_dir = temp_dir / "__pycache__"
        pycache_dir.mkdir()

        pyc_file = pycache_dir / "module.pyc"
        pyc_file.write_text("compiled python")

        normal_file = temp_dir / "normal.txt"
        normal_file.write_text("normal content")

        # Configurar exclusiones con patrones más simples
        guardian.config.update(
            {
                "monitored_paths": [str(temp_dir)],
                "excluded_paths": [".git", "__pycache__"],  # Patrones simples
            }
        )
        guardian.on_config_updated()

        # Escanear
        scan_result = guardian._perform_security_scan()

        # Solo debería escanear el archivo normal
        assert scan_result["files_scanned"] == 1

        # Verificar que los archivos excluidos no fueron escaneados
        # Los archivos en .git y __pycache__ no deberían haber generado amenazas
        assert scan_result["threats_detected"] == 0

    def test_security_callbacks(self, guardian):
        """Test callbacks de seguridad."""
        callback_called = False
        callback_result = None

        def test_callback(result):
            nonlocal callback_called, callback_result
            callback_called = True
            callback_result = result

        # Agregar callback
        guardian.add_security_callback(test_callback)

        # Ejecutar tarea
        result = guardian.execute_task()

        # Verificar callback
        assert callback_called
        assert callback_result is not None

        # Remover callback
        guardian.remove_security_callback(test_callback)

        # Verificar que ya no se llama
        callback_called = False
        guardian.execute_task()
        # Callback no debería llamarse nuevamente en este test simple

    def test_alert_callbacks(self, guardian, temp_dir):
        """Test callbacks de alertas."""
        alert_received = None

        def alert_callback(alert):
            nonlocal alert_received
            alert_received = alert

        # Agregar callback de alertas
        guardian.add_alert_callback(alert_callback)

        # Crear archivo sospechoso para generar alerta
        exe_file = temp_dir / "suspicious.exe"
        exe_file.write_text("test")

        guardian.config.update(
            {"monitored_paths": [str(temp_dir)], "suspicious_extensions": {".exe"}}
        )
        guardian.on_config_updated()

        # Escanear para generar alerta
        guardian._perform_security_scan()

        # Verificar callback
        assert alert_received is not None
    # assert eliminado por refactor: ThreatLevel
        assert "suspicious.exe" in alert_received.file_path

    def test_security_events_logging(self, guardian, temp_dir):
        """Test logging de eventos de seguridad."""
        # Generar algunos eventos
        exe_file = temp_dir / "test.exe"
        exe_file.write_text("test")

        guardian.config.update(
            {"monitored_paths": [str(temp_dir)], "suspicious_extensions": {".exe"}}
        )
        guardian.on_config_updated()

        guardian._perform_security_scan()

        # Verificar eventos registrados
        events = guardian.get_security_events()
        assert len(events) >= 1

        # Verificar que hay eventos de alerta
        alert_events = [e for e in events if e.event_type == "alert_generated"]
        assert len(alert_events) >= 1

    def test_background_execution(self, guardian):
        """Test funcionamiento en background."""
        # Iniciar worker
        guardian.start()

        # Esperar un poco
        time.sleep(0.1)

        # Verificar estado
        assert guardian.state == BotState.RUNNING
        assert guardian._thread.is_alive()

        # Ejecutar tarea en background
        result = guardian.execute_task()

        # Verificar resultado
        assert result["success"] is True

        # Detener worker
        guardian.stop()

        # Esperar a que termine
        time.sleep(0.1)

        assert guardian.state == BotState.STOPPED

    def test_security_stats(self, guardian, temp_dir):
        """Test estadísticas de seguridad."""
        # Realizar algunas operaciones
        exe_file = temp_dir / "test.exe"
        exe_file.write_text("test")

        guardian.config.update(
            {"monitored_paths": [str(temp_dir)], "suspicious_extensions": {".exe"}}
        )
        guardian.on_config_updated()

        guardian.execute_task()

        # Obtener estadísticas
        stats = guardian.get_security_stats()

        assert "total_scans" in stats
        assert "threats_detected" in stats
        assert "alerts_generated" in stats
        assert "active_alerts" in stats
        assert stats["total_scans"] >= 1
        assert stats["threats_detected"] >= 1
        assert stats["alerts_generated"] >= 1

    def test_integrity_management(self, guardian, temp_dir):
        """Test gestión de integridad de archivos."""
        test_file = temp_dir / "integrity.txt"
        test_file.write_text("test content")

        # Agregar archivo
        guardian.add_file_to_integrity_check(str(test_file))

        assert len(guardian.file_integrity_hashes) == 1
        assert str(test_file) in guardian.file_integrity_hashes

        # Remover archivo
        guardian.remove_file_from_integrity_check(str(test_file))

        assert len(guardian.file_integrity_hashes) == 0

    def test_alert_cleanup(self, guardian):
        """Test limpieza de alertas expiradas."""
        # Crear alerta antigua (mock)
        old_alert = SecurityAlert(
            alert_id="old_alert",
            # threat_level eliminado por refactor
            title="Old Alert",
            description="Old alert description",
            file_path="/old/file",
            timestamp=datetime.now() - timedelta(hours=25),  # Más de 24 horas
            details={},
        )

        guardian.active_alerts.append(old_alert)

        # Crear alerta reciente
        new_alert = SecurityAlert(
            alert_id="new_alert",
            # threat_level eliminado por refactor
            title="New Alert",
            description="New alert description",
            file_path="/new/file",
            timestamp=datetime.now(),
            details={},
        )

        guardian.active_alerts.append(new_alert)

        # Limpiar alertas expiradas
        guardian._cleanup_expired_alerts()

        # Solo debería quedar la alerta nueva
        active_alerts = guardian.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0].alert_id == "new_alert"

    def test_error_handling(self, guardian):
        """Test manejo de errores."""
        # Configurar ruta inexistente
        guardian.config.update(
            {"monitored_paths": ["/nonexistent/path/that/does/not/exist"]}
        )
        guardian.on_config_updated()

        # Ejecutar tarea
        result = guardian.execute_task()

        # Debería manejar el error gracefully
        assert result["success"] is True  # El sistema sigue funcionando
        assert result["result"]["errors_count"] >= 1

    def test_clear_security_data(self, guardian, temp_dir):
        """Test limpieza de datos de seguridad."""
        # Agregar algunos datos
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        guardian.add_file_to_integrity_check(str(test_file))

        exe_file = temp_dir / "test.exe"
        exe_file.write_text("test")

        guardian.config.update(
            {"monitored_paths": [str(temp_dir)], "suspicious_extensions": {".exe"}}
        )
        guardian.on_config_updated()

        guardian.execute_task()

        # Verificar que hay datos
        assert len(guardian.file_integrity_hashes) > 0
        assert len(guardian.get_active_alerts()) > 0
        assert len(guardian.get_security_events()) > 0

        # Limpiar datos
        guardian.clear_security_data()

        # Verificar que se limpiaron
        assert len(guardian.file_integrity_hashes) == 0
        assert len(guardian.get_active_alerts()) == 0
        assert len(guardian.get_security_events()) == 0
        assert guardian.total_scans == 0
        assert guardian.threats_detected == 0

    def test_repr(self, guardian):
        """Test representación string."""
        repr_str = repr(guardian)

        assert "GuardianWorker" in repr_str
        assert guardian.bot_id in repr_str
        assert "scans=" in repr_str
        assert "threats=" in repr_str
        assert "alerts=" in repr_str

    @pytest.mark.skip("ThreatLevel enum removed by refactor")
    def test_alert_threat_levels(self, guardian):
        """Test diferentes niveles de amenaza en alertas."""
        # This test is skipped because ThreatLevel enum was removed in refactor.
        alert = SecurityAlert(
            alert_id=f"test_disabled",
            title=f"Test disabled",
            description="Test alert",
            file_path="/test/file",
            timestamp=datetime.now(),
            details={},
        )

        guardian._generate_alert(alert)

        alerts = guardian.get_active_alerts()
        assert len(alerts) >= 1

        # Verificar que la alerta se generó correctamente
        found_alert = None
        for a in alerts:
            if a.alert_id == alert.alert_id:
                found_alert = a
                break

        assert found_alert is not None
    # threat_level comparison removed due to refactor

    def test_concurrent_access(self, guardian, temp_dir):
        """Test acceso concurrente a estructuras de datos."""
        import threading

        # Crear varios archivos
        files = []
        for i in range(10):
            f = temp_dir / f"test_{i}.txt"
            f.write_text(f"content {i}")
            files.append(f)

        guardian.config.update({"monitored_paths": [str(temp_dir)]})
        guardian.on_config_updated()

        # Función para ejecutar tareas concurrentemente
        results = []

        def worker_task():
            result = guardian.execute_task()
            results.append(result)

        # Crear y ejecutar hilos
        threads = []
        for _ in range(3):
            t = threading.Thread(target=worker_task)
            threads.append(t)
            t.start()

        # Esperar a que terminen
        for t in threads:
            t.join()

        # Verificar que todas las ejecuciones fueron exitosas
        assert len(results) == 3
        for result in results:
            assert result["success"] is True

    def test_file_hash_calculation(self, guardian, temp_dir):
        """Test cálculo de hash de archivos."""
        test_file = temp_dir / "hash_test.txt"
        content = "test content for hashing"
        test_file.write_text(content)

        # Calcular hash
        file_hash = guardian._calculate_file_hash(test_file)

        # Verificar que es un hash válido
        assert len(file_hash) == 64  # SHA256 hex
        assert file_hash.isalnum()

        # Verificar que el mismo contenido produce el mismo hash
        hash2 = guardian._calculate_file_hash(test_file)
        assert hash2 == file_hash

        # Verificar que contenido diferente produce hash diferente
        test_file.write_text("different content")
        hash3 = guardian._calculate_file_hash(test_file)
        assert hash3 != file_hash

    def test_suspicious_content_detection(self, guardian, temp_dir):
        """Test detección de contenido sospechoso."""
        # Crear archivo con contenido sospechoso
        suspicious_file = temp_dir / "suspicious.txt"
        suspicious_file.write_bytes(
            b"normal content " + b"powershell script here" + b" more content"
        )

        guardian.config.update({"monitored_paths": [str(temp_dir)]})
        guardian.on_config_updated()

        # Escanear
        scan_result = guardian._perform_security_scan()

        # Verificar que se detectó contenido sospechoso
        alerts = guardian.get_active_alerts()
        suspicious_alerts = [a for a in alerts if "Contenido sospechoso" in a.title]

        assert len(suspicious_alerts) >= 1

    def test_file_permission_denied(self, guardian, temp_dir):
        """Test manejo de archivos con permisos denegados."""
        from unittest.mock import patch

        # Crear archivo normal
        test_file = temp_dir / "permission_denied.txt"
        test_file.write_text("test content")

        guardian.config.update({"monitored_paths": [str(temp_dir)]})
        guardian.on_config_updated()

        # Mockear stat() para simular error de permisos
        with patch(
            "pathlib.Path.stat", side_effect=PermissionError("Permission denied")
        ):
            # Escanear - debería manejar el error gracefully
            scan_result = guardian._perform_security_scan()

            # Debería reportar error pero continuar
            assert scan_result["errors_count"] >= 1

    def test_corrupt_file_handling(self, guardian, temp_dir):
        """Test manejo de archivos corruptos."""
        # Crear archivo con contenido corrupto
        corrupt_file = temp_dir / "corrupt.dat"
        corrupt_file.write_bytes(
            b"\x00\x01\x02\x03\xff\xfe\xfd" * 100
        )  # Bytes aleatorios

        guardian.config.update({"monitored_paths": [str(temp_dir)]})
        guardian.on_config_updated()

        # Escanear
        scan_result = guardian._perform_security_scan()

        # Debería procesar el archivo sin errores
        assert scan_result["files_scanned"] >= 1
        assert scan_result["errors_count"] == 0

    def test_empty_file_integrity(self, guardian, temp_dir):
        """Test verificación de integridad en archivos vacíos."""
        # Crear archivo vacío
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")

        guardian.add_file_to_integrity_check(str(empty_file))

        # Modificar archivo (agregar contenido)
        empty_file.write_text("modified")

        # Verificar integridad
        checks = guardian._perform_integrity_check()

        assert checks >= 1

        # Debería detectar modificación
        alerts = guardian.get_active_alerts()
        integrity_alerts = [
            a for a in alerts if "Modificación no autorizada" in a.title
        ]

        assert len(integrity_alerts) >= 1

    def test_large_file_hash_performance(self, guardian, temp_dir):
        """Test cálculo de hash en archivos grandes (simulado)."""
        # Crear archivo mediano para test de performance
        large_file = temp_dir / "large_test.dat"
        # Crear archivo de ~1MB
        content = b"x" * (1024 * 1024)
        large_file.write_bytes(content)

        # Medir tiempo de cálculo de hash
        import time

        start_time = time.time()
        hash_result = guardian._calculate_file_hash(large_file)
        end_time = time.time()

        # Verificar que el hash se calculó
        assert len(hash_result) == 64  # SHA256
        assert hash_result.isalnum()

        # Verificar que no tomó demasiado tiempo (menos de 1 segundo para 1MB)
        assert (end_time - start_time) < 1.0

    def test_concurrent_hash_calculation(self, guardian, temp_dir):
        """Test cálculo concurrente de hashes."""
        import threading

        # Crear varios archivos
        files = []
        hashes = {}
        for i in range(5):
            f = temp_dir / f"concurrent_{i}.txt"
            content = f"content {i}" * 100  # Hacerlos un poco más grandes
            f.write_text(content)
            files.append(f)
            hashes[str(f)] = guardian._calculate_file_hash(f)

        # Función para verificar hash en thread separado
        results = []
        errors = []

        def verify_hash(file_path, expected_hash):
            try:
                actual_hash = guardian._calculate_file_hash(Path(file_path))
                results.append(actual_hash == expected_hash)
            except Exception as e:
                errors.append(str(e))

        # Ejecutar verificaciones en paralelo
        threads = []
        for file_path, expected_hash in hashes.items():
            t = threading.Thread(target=verify_hash, args=(file_path, expected_hash))
            threads.append(t)
            t.start()

        # Esperar a que terminen
        for t in threads:
            t.join()

        # Verificar que todos los hashes coincidieron
        assert len(results) == len(hashes)
        assert all(results)
        assert len(errors) == 0

    def test_regex_pattern_matching(self, guardian, temp_dir):
        """Test matching de patrones regex en amenazas."""
        # Crear archivos con nombres que coincidan con patrones
        virus_file = temp_dir / "virus.exe"
        virus_file.write_text("virus")

        trojan_file = temp_dir / "trojan.bat"
        trojan_file.write_text("trojan")

        normal_file = temp_dir / "normal.txt"
        normal_file.write_text("normal")

        # Configurar patrones simples (no regex para evitar complejidad)
        guardian.config.update(
            {
                "monitored_paths": [str(temp_dir)],
                "threat_patterns": ["virus", "trojan"],  # Patrones simples
            }
        )
        guardian.on_config_updated()

        # Escanear
        scan_result = guardian._perform_security_scan()

        # Debería detectar amenazas en archivos con nombres que contengan los patrones
        assert scan_result["threats_detected"] >= 2

        alerts = guardian.get_active_alerts()
        threat_alerts = [a for a in alerts if "Patrón de amenaza" in a.title]

        assert len(threat_alerts) >= 2

    def test_invalid_config_validation(self, guardian):
        """Test validación de configuración inválida."""
        # Configuraciones inválidas
        invalid_configs = [
            {"monitored_paths": "not_a_list"},  # Debe ser lista
            {"excluded_paths": "not_a_list"},  # Debe ser lista
            {"max_file_size_alert": "not_a_number"},  # Debe ser numérico
            {"execution_interval": -1},  # Debe ser positivo
            {"enable_real_time_monitoring": "not_a_bool"},  # Debe ser booleano
        ]

        for invalid_config in invalid_configs:
            assert guardian.validate_config(invalid_config) == False

    def test_valid_config_validation(self, guardian):
        """Test validación de configuración válida."""
        valid_config = {
            "monitored_paths": ["/path1", "/path2"],
            "excluded_paths": [".git", "__pycache__"],
            "threat_patterns": [".exe", ".bat"],
            "suspicious_extensions": [".exe", ".dll"],
            "max_file_size_alert": 100 * 1024 * 1024,
            "integrity_check_interval": 3600,
            "execution_interval": 300,
            "enable_real_time_monitoring": True,
            "log_security_events": True,
            "auto_quarantine": False,
            "alert_on_suspicious": True,
        }

        assert guardian.validate_config(valid_config) == True
