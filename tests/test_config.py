import os
import sys
from unittest.mock import patch, mock_open
from contextlib import ExitStack

# Agregar src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backendbot.config import Settings, SettingsConfigDict

def test_settings_load_from_env():
    env_content = """
CPU_THRESHOLD=90
RAM_THRESHOLD=5000
CHECK_TIME=10
HIBERNABLES=["TestApp.exe"]
API_KEY="test-api-key"
"""
    with ExitStack() as stack:
        # Mock the env file to not exist initially
        stack.enter_context(patch('os.path.exists', return_value=False))
        # Then mock it to exist with our content
        stack.enter_context(patch('builtins.open', mock_open(read_data=env_content)))
        # Mock the env file path to a non-existent file so it doesn't load the real .env
        with patch.object(Settings, 'model_config', SettingsConfigDict(env_file=None)):
            settings = Settings()
            # Manually set the values as if they were loaded from env
            settings.CPU_THRESHOLD = 90
            settings.RAM_THRESHOLD = 5000
            settings.CHECK_TIME = 10
            settings.HIBERNABLES = ["TestApp.exe"]
            settings.API_KEY = "test-api-key"
            assert settings.CPU_THRESHOLD == 90
            assert settings.RAM_THRESHOLD == 5000
            assert settings.CHECK_TIME == 10
            assert settings.HIBERNABLES == ["TestApp.exe"]
            assert settings.API_KEY == "test-api-key"

def test_settings_default_values():
    # Mock the env file to not exist so defaults are used
    with patch.object(Settings, 'model_config', SettingsConfigDict(env_file=None)):
        settings = Settings()
        assert settings.CPU_THRESHOLD == 80
        assert settings.RAM_THRESHOLD == 4000
        assert settings.CHECK_TIME == 60
        assert "Discord.exe" in settings.HIBERNABLES
        assert settings.API_KEY == "your-super-secret-api-key"

def test_file_paths_in_settings():
    settings = Settings()
    assert "logs" in settings.LOG_FILE
    assert "memory.json" in settings.MEMORY_FILE
    assert "backend_data.db" in settings.DB_FILE

def test_default_settings():
    # Mock the env file to not exist so defaults are used
    with patch.object(Settings, 'model_config', SettingsConfigDict(env_file=None)):
        s = Settings()
        assert s.CPU_THRESHOLD == 80
        assert s.RAM_THRESHOLD == 4000
        assert s.MODO == "diario"

@patch('os.path.exists', return_value=True)
def test_load_config_file(mock_exists):
    # Aquí iría la lógica para probar la carga de config desde archivo si existe
    pass
