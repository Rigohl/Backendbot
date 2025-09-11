import os
import sys
import json
from unittest.mock import patch, mock_open, MagicMock

# Agregar src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backendbot.utils import notify, log_event, load_memory, save_memory
from backendbot.config import Settings

# Mock settings for utils
@patch('backendbot.utils.settings', Settings())
@patch('backendbot.utils.ToastNotifier')
def test_notify(mock_toaster):
    notify("Test message")
    mock_toaster.return_value.show_toast.assert_called_once_with("BackendBot", "Test message", duration=4, threaded=True)

@patch('backendbot.utils.settings', Settings())
@patch('os.makedirs')
@patch('builtins.open', new_callable=mock_open)
@patch('backendbot.utils.notify')
def test_log_event(mock_notify, mock_open, mock_makedirs):
    log_event("Log message")
    mock_makedirs.assert_called_once()
    mock_open.assert_called_once_with(Settings().LOG_FILE, "a", encoding="utf-8")
    handle = mock_open()
    handle.write.assert_called_once()
    assert "Log message" in handle.write.call_args[0][0]

    log_event("Log message with notify", notify_user=True)
    mock_notify.assert_called_once_with("Log message with notify")

@patch('backendbot.utils.settings', Settings())
@patch('os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
def test_load_memory(mock_open, mock_exists):
    memory = load_memory()
    assert memory == {"key": "value"}

@patch('backendbot.utils.settings', Settings())
@patch('os.path.exists', return_value=False)
def test_load_memory_no_file(mock_exists):
    memory = load_memory()
    assert memory == {}

@patch('backendbot.utils.settings', Settings())
@patch('builtins.open', new_callable=mock_open)
def test_save_memory(mock_open):
    memory_data = {"new_key": "new_value"}
    save_memory(memory_data)
    mock_open.assert_called_once_with(Settings().MEMORY_FILE, "w", encoding="utf-8")
    handle = mock_open()
    handle.write.assert_called_once_with(json.dumps(memory_data, indent=2))
