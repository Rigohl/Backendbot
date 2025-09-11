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


def test_settings_apply_defaults(clear_env_vars):
    """Verify that default values are used when env vars are not set."""
    # We must provide the one required variable, API_KEY
    with patch.dict(os.environ, {"API_KEY": "required_default_test_key"}):
        settings = Settings()

        # Check default values from the Settings class
        assert settings.MODO == "diario"
        assert settings.CPU_THRESHOLD == 80
        assert settings.RAM_THRESHOLD == 4000
        assert settings.HIBERNABLES == []
        assert settings.PROCESOS_A_CERRAR == {}
        assert settings.PROCESOS_IMPORTANTES == []


def test_settings_fail_without_required_fields(clear_env_vars):
    """Verify that creating settings fails if a required field (API_KEY) is missing."""
    with pytest.raises(ValueError):
        # Instantiating should fail because API_KEY is not in the environment
        Settings()


def test_file_paths_are_correctly_constructed():
    """Verify that file paths are constructed correctly relative to the project root."""
    with patch.dict(os.environ, {"API_KEY": "path_test_key"}):
        settings = Settings()

        assert settings.LOG_FILE == EXPECTED_BASE_DIR / "logs" / "backend.log"
        assert settings.MEMORY_FILE == EXPECTED_BASE_DIR / "memory.json"
        # Check the default database path construction
        expected_db_path = f"sqlite:///{EXPECTED_BASE_DIR / 'data' / 'backend_data.db'}"
        assert settings.DATABASE_URL == expected_db_path


def test_invalid_json_string_in_env_raises_error():
    """Verify that a malformed JSON string in an env var raises a ValueError."""
    # Malformed JSON (missing closing bracket)
    mock_vars = {"API_KEY": "json_test_key", "HIBERNABLES": '["test.exe"'}
    with patch.dict(os.environ, mock_vars):
        with pytest.raises(ValueError, match="Invalid JSON string provided for configuration"):
            Settings()