"""
Tests para el sistema de bots BackendBot
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Importar los módulos de bots
from backendbot.bots.manager import BotManager
from backendbot.bots.monitor import MonitorBot
from backendbot.bots.organizer import OrganizerBot
from backendbot.bots.indexer import IndexerBot
from backendbot.bots.chat import ChatBot


class TestBotManager:
    """Tests para BotManager"""

    def setup_method(self):
        """Configurar antes de cada test"""
        self.manager = BotManager()

    def test_initialization(self):
        """Test que el manager se inicializa correctamente"""
        assert self.manager is not None
        assert hasattr(self.manager, 'bots')
        assert isinstance(self.manager.bots, dict)

    def test_load_bots(self):
        """Test que carga todos los bots correctamente"""
        self.manager._load_bots()
        # Solo carga los 5 bots canónicos inicialmente
        expected_bots = ['monitor', 'organizer', 'indexer', 'guardian', 'optimizer']
        for bot_name in expected_bots:
            assert bot_name in self.manager.bots
            assert self.manager.bots[bot_name] is not None

    def test_process_command_valid(self):
        """Test procesamiento de comandos válidos"""
        self.manager._load_bots()
        # Mockear la función get_db global
        with patch('backendbot.bots.manager.get_db') as mock_get_db:
            mock_session = Mock()
            mock_get_db.return_value.__enter__.return_value = mock_session
            result = self.manager.process_command("monitor status")
            assert result is not None
            assert isinstance(result, str)

    def test_process_command_invalid(self):
        """Test procesamiento de comandos inválidos"""
        self.manager._load_bots()
        # Mockear la función get_db global
        with patch('backendbot.bots.manager.get_db') as mock_get_db:
            mock_session = Mock()
            mock_get_db.return_value.__enter__.return_value = mock_session
            result = self.manager.process_command("invalid command")
            # Cuando no hay bot chat, debería devolver mensaje de bot no disponible
            assert "no disponible" in result.lower() or "desconocido" in result.lower()


class TestMonitorBot:
    """Tests para MonitorBot"""

    def setup_method(self):
        """Configurar antes de cada test"""
        self.bot = MonitorBot()

    def test_initialization(self):
        """Test que el bot se inicializa correctamente"""
        assert self.bot is not None
        assert hasattr(self.bot, 'execute')

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.net_io_counters')
    def test_monitor_system(self, mock_net, mock_disk, mock_memory, mock_cpu):
        """Test monitoreo del sistema"""
        # Configurar mocks
        mock_cpu.return_value = 45.5
        mock_memory.return_value.percent = 60.0
        mock_memory.return_value.used = 4 * 1024**3  # 4GB
        mock_disk.return_value.percent = 75.0
        mock_disk.return_value.used = 100 * 1024**3  # 100GB
        mock_net.return_value.bytes_sent = 500 * 1024**2  # 500MB
        mock_net.return_value.bytes_recv = 200 * 1024**2  # 200MB

        result = self.bot.execute("monitor")
        assert "Monitoreo del Sistema" in result
        assert "45.5%" in result
        assert "60.0%" in result
        assert "75.0%" in result

    @patch('psutil.process_iter')
    def test_get_processes(self, mock_process_iter):
        """Test obtención de procesos"""
        # Crear mock de proceso
        mock_proc = Mock()
        mock_proc.info = {'pid': 123, 'name': 'test.exe', 'cpu_percent': 5.0, 'memory_percent': 2.0}
        mock_process_iter.return_value = [mock_proc]

        result = self.bot.execute("processes")
        assert "Procesos principales" in result
        assert "test.exe" in result
        assert "CPU 5.0%" in result
        assert "RAM 2.0%" in result


class TestOrganizerBot:
    """Tests para OrganizerBot"""

    def setup_method(self):
        """Configurar antes de cada test"""
        self.bot = OrganizerBot()
        # Crear directorio temporal para tests
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Limpiar después de cada test"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization(self):
        """Test que el bot se inicializa correctamente"""
        assert self.bot is not None
        assert hasattr(self.bot, 'execute')

    def test_organize_by_type(self):
        """Test organización de archivos por tipo"""
        # Crear archivos de prueba en el directorio de descargas del usuario
        downloads_dir = Path.home() / "Downloads"
        if not downloads_dir.exists():
            downloads_dir.mkdir()

        # Crear archivos de prueba
        txt_file = downloads_dir / "test_organizer.txt"
        jpg_file = downloads_dir / "image_organizer.jpg"
        pdf_file = downloads_dir / "doc_organizer.pdf"

        try:
            with open(txt_file, 'w') as f:
                f.write("test")
            with open(jpg_file, 'w') as f:
                f.write("fake jpg")
            with open(pdf_file, 'w') as f:
                f.write("fake pdf")

            result = self.bot.execute("organize")

            # Verificar que se crearon las carpetas
            assert (downloads_dir / "Documentos").exists() or (downloads_dir / "Archivos").exists() or (downloads_dir / "Imágenes").exists()

        finally:
            # Limpiar archivos de prueba
            for file in [txt_file, jpg_file, pdf_file]:
                if file.exists():
                    file.unlink()
            # Limpiar directorios creados si existen
            for dir_name in ["Documentos", "Imágenes", "Archivos"]:
                dir_path = downloads_dir / dir_name
                if dir_path.exists():
                    try:
                        shutil.rmtree(dir_path)
                    except:
                        pass


class TestIndexerBot:
    """Tests para IndexerBot"""

    def setup_method(self):
        """Configurar antes de cada test"""
        self.bot = IndexerBot()
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Limpiar después de cada test"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization(self):
        """Test que el bot se inicializa correctamente"""
        assert self.bot is not None
        assert hasattr(self.bot, 'execute')

    def test_build_index(self):
        """Test construcción de índice de archivos"""
        result = self.bot.execute("index")
        assert len(result) > 0
        assert "índice" in result.lower() or "archivos" in result.lower()

    def test_find_duplicates(self):
        """Test búsqueda de archivos duplicados"""
        result = self.bot.execute("find_duplicates")
        assert "duplicados" in result.lower() or "duplicates" in result.lower()


class TestChatBot:
    """Tests para ChatBot"""

    def setup_method(self):
        """Configurar antes de cada test"""
        self.bot = ChatBot()

    def test_initialization(self):
        """Test que el bot se inicializa correctamente"""
        assert self.bot is not None
        assert hasattr(self.bot, 'execute')

    def test_interpret_natural_language_duplicates(self):
        """Test interpretación de comando para buscar duplicados"""
        result = self.bot.execute("buscame archivos duplicados")
        assert "duplicados" in result.lower() or "duplicates" in result.lower()

    def test_interpret_natural_language_unused_files(self):
        """Test interpretación de comando para buscar archivos no utilizados"""
        result = self.bot.execute("busca archivos que no he utilizado")
        assert "utilizado" in result.lower() or "used" in result.lower()

    def test_interpret_natural_language_programs(self):
        """Test interpretación de comando para buscar programas no usados"""
        result = self.bot.execute("busca programas que no use")
        assert "programas" in result.lower() or "programs" in result.lower()

    def test_interpret_unknown_command(self):
        """Test interpretación de comando desconocido"""
        result = self.bot.execute("comando completamente desconocido")
        assert "no entiendo" in result.lower() or "desconocido" in result.lower()


if __name__ == "__main__":
    pytest.main([__file__])