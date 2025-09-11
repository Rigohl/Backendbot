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
@patch('win10toast.ToastNotifier')
def test_notify(mock_toaster):
    notify("Test Title", "Test message")
    mock_toaster.return_value.show_toast.assert_called_once_with("Test Title", "Test message", duration=5)

@patch('backendbot.utils.settings', Settings())
@patch('os.makedirs')
@patch('builtins.open', new_callable=mock_open)
@patch('backendbot.utils.notify')
def test_log_event(mock_notify, mock_open, mock_makedirs):
    # Mock the env file loading to avoid interference
    with patch('os.path.exists', return_value=False):
        log_event("Log message")
        # Find the call to the log file specifically
        log_file_calls = [call for call in mock_open.call_args_list if str(Settings().LOG_FILE) in str(call)]
        assert len(log_file_calls) == 1
        mock_makedirs.assert_called_once()
        mock_open.assert_called()
        assert "Log message" in str(mock_open().write.call_args_list)

    with patch('os.path.exists', return_value=False):
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
    # Mock the env file loading to avoid interference
    with patch('os.path.exists', return_value=False):
        memory_data = {"new_key": "new_value"}
        save_memory(memory_data)
        # Find the call to the memory file specifically
        memory_file_calls = [call for call in mock_open.call_args_list if str(Settings().MEMORY_FILE) in str(call)]
        assert len(memory_file_calls) == 1
        # Verify that write was called (json.dump calls it multiple times)
        assert mock_open().write.called
