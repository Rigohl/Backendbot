"""
Tests for the centralized configuration system (src/backendbot/config.py).

This module verifies that the Pydantic Settings model correctly loads configuration
from environment variables, including complex JSON strings, and applies default
values when variables are not set.
"""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from backendbot.config import Settings

# The BASE_DIR from the config module we are testing
EXPECTED_BASE_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture
def mock_env_vars():
    """Fixture to set up mock environment variables for testing."""
    # Simple key-value pairs
    mock_vars = {
        "API_KEY": "test-suite-api-key",
        "MODO": "videojuego",
        "CPU_THRESHOLD": "99",
        "RAM_THRESHOLD": "1234",
        "DATABASE_URL": "sqlite:///test.db",
        # Complex values as JSON strings
        "HIBERNABLES": '["test.exe", "mock.exe"] ',
        "PROCESOS_A_CERRAR": '{"test_mode": ["process1.exe"]}',
        "PROCESOS_IMPORTANTES": '["kernel.exe"]'
    }
    with patch.dict(os.environ, mock_vars):
        yield


@pytest.fixture
def clear_env_vars():
    """Fixture to clear relevant environment variables to test defaults."""
    env_keys_to_clear = [
        "API_KEY",
        "MODO",
        "CPU_THRESHOLD",
        "RAM_THRESHOLD",
        "DATABASE_URL",
        "HIBERNABLES",
        "PROCESOS_A_CERRAR",
        "PROCESOS_IMPORTANTES",
    ]
    original_values = {key: os.environ.get(key) for key in env_keys_to_clear}
    
    # Clear the keys for the duration of the test
    for key in env_keys_to_clear:
        if key in os.environ:
            del os.environ[key]
    
    yield
    
    # Restore original values
    for key, value in original_values.items():
        if value is not None:
            os.environ[key] = value

# --- Test Cases ---

def test_settings_load_from_mock_env(mock_env_vars):
    """Verify that settings are correctly loaded from environment variables."""
    settings = Settings()

    assert settings.API_KEY == "test-suite-api-key"
    assert settings.MODO == "videojuego"
    assert settings.CPU_THRESHOLD == 99
    assert settings.RAM_THRESHOLD == 1234
    assert settings.DATABASE_URL == "sqlite:///test.db"
    assert settings.HIBERNABLES == ["test.exe", "mock.exe"]
    assert settings.PROCESOS_A_CERRAR == {"test_mode": ["process1.exe"]}
    assert settings.PROCESOS_IMPORTANTES == ["kernel.exe"]


import os
import pytest
from unittest.mock import patch
from src.backendbot.config import Settings


def test_settings_default_values():
    with patch.dict(os.environ, {"API_KEY": "test_key"}):
        settings = Settings()
        assert settings.CPU_THRESHOLD == 80
        assert settings.RAM_THRESHOLD == 4000
        assert settings.CHECK_TIME == 60
        assert settings.MODO == "diario"
        assert settings.API_KEY == "test_key"


def test_settings_validation():
    with patch.dict(os.environ, {"API_KEY": "test_key"}):
        # Valid values
        settings = Settings(CPU_THRESHOLD=50, RAM_THRESHOLD=2000)
        assert settings.CPU_THRESHOLD == 50
        assert settings.RAM_THRESHOLD == 2000

        # Invalid CPU threshold
        with pytest.raises(ValueError):
            Settings(CPU_THRESHOLD=150, API_KEY="test_key")

        # Invalid RAM threshold
        with pytest.raises(ValueError):
            Settings(RAM_THRESHOLD=50, API_KEY="test_key")


def test_settings_process_lists():
    with patch.dict(os.environ, {"API_KEY": "test_key"}):
        settings = Settings()
        assert "Discord.exe" in settings.HIBERNABLES
        assert "videojuego" in settings.PROCESOS_A_CERRAR
        assert "explorer.exe" in settings.PROCESOS_IMPORTANTES


def test_settings_file_paths():
    with patch.dict(os.environ, {"API_KEY": "test_key"}):
        settings = Settings()
        assert "logs" in settings.LOG_FILE
        assert "memory.json" in settings.MEMORY_FILE
        assert "backend_data.db" in settings.DATABASE_URL


def test_settings_optional_dependencies():
    with patch.dict(os.environ, {"API_KEY": "test_key"}):
        settings = Settings()
        # These should be boolean flags
        assert isinstance(settings.GPU_AVAILABLE, bool)
        assert isinstance(settings.WMI_AVAILABLE, bool)


def test_settings_env_override():
    with patch.dict(os.environ, {
        "API_KEY": "env_key",
        "CPU_THRESHOLD": "70",
        "DATABASE_URL": "sqlite:///test.db"
    }):
        settings = Settings()
        assert settings.API_KEY == "env_key"
        assert settings.CPU_THRESHOLD == 70
        assert "test.db" in settings.DATABASE_URL


def test_settings_jwt_config():
    with patch.dict(os.environ, {"API_KEY": "test_key"}):
        settings = Settings()
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert settings.JWT_SECRET_KEY == "your-secret-key"


def test_settings_rate_limiting():
    with patch.dict(os.environ, {"API_KEY": "test_key"}):
        settings = Settings()
        assert settings.RATE_LIMIT_REQUESTS == 100
        assert settings.RATE_LIMIT_WINDOW == 60


def test_settings_fail_without_required_fields(clear_env_vars):
    """Verify that creating settings works with default API_KEY."""
    # Since API_KEY now has a default value, this should work
    settings = Settings()
    assert settings.API_KEY == "default-api-key"


def test_file_paths_are_correctly_constructed():
    """Verify that file paths are constructed correctly relative to the project root."""
    with patch.dict(os.environ, {"API_KEY": "path_test_key"}):
        settings = Settings()

        assert str(settings.LOG_FILE).endswith("logs\\backend.log")
        assert str(settings.MEMORY_FILE).endswith("memory.json")
        # Check the default database path construction
        assert "sqlite:///" in settings.DATABASE_URL


def test_invalid_json_string_in_env_raises_error():
    """Verify that a malformed JSON string in an env var raises a ValueError."""
    # Malformed JSON (missing closing bracket)
    mock_vars = {"API_KEY": "json_test_key", "HIBERNABLES": '["test.exe"'}
    with patch.dict(os.environ, mock_vars):
        with pytest.raises(ValueError, match="error parsing value for field"):
            Settings()