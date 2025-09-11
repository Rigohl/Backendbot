import os
import json
from unittest.mock import patch, mock_open, MagicMock
from src.backendbot.refactored_modules.utils import notify, log_event, load_memory, save_memory, store_process_data, store_optimization_event, store_watchdog_decision, restore_closed_processes
from src.backendbot.refactored_modules.config import Settings

# Mock settings for utils
@patch('src.backendbot.refactored_modules.utils.settings', Settings())
@patch('src.backendbot.refactored_modules.utils.ToastNotifier')
def test_notify(mock_toaster):
    notify("Test message")
    mock_toaster.return_value.show_toast.assert_called_once_with("BackendBot", "Test message", duration=4, threaded=True)

@patch('src.backendbot.refactored_modules.utils.settings', Settings())
@patch('os.makedirs')
@patch('builtins.open', new_callable=mock_open)
@patch('src.backendbot.refactored_modules.utils.notify')
def test_log_event(mock_notify, mock_open, mock_makedirs):
    log_event("Log message")
    mock_makedirs.assert_called_once()
    mock_open.assert_called_once_with(Settings().LOG_FILE, "a", encoding="utf-8")
    handle = mock_open()
    handle.write.assert_called_once()
    assert "Log message" in handle.write.call_args[0][0]

    log_event("Log message with notify", notify_user=True)
    mock_notify.assert_called_once_with("Log message with notify")

@patch('src.backendbot.refactored_modules.utils.settings', Settings())
@patch('os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
def test_load_memory(mock_open, mock_exists):
    memory = load_memory()
    assert memory == {"key": "value"}

@patch('src.backendbot.refactored_modules.utils.settings', Settings())
@patch('os.path.exists', return_value=False)
def test_load_memory_no_file(mock_exists):
    memory = load_memory()
    assert memory == {}

@patch('src.backendbot.refactored_modules.utils.settings', Settings())
@patch('builtins.open', new_callable=mock_open)
def test_save_memory(mock_open):
    memory_data = {"new_key": "new_value"}
    save_memory(memory_data)
    mock_open.assert_called_once_with(Settings().MEMORY_FILE, "w", encoding="utf-8")
    handle = mock_open()
    handle.write.assert_called_once_with(json.dumps(memory_data, indent=2))

@patch('src.backendbot.refactored_modules.utils.db')
def test_store_process_data(mock_db):
    store_process_data(123, "test_process", 100.5, 50.2)
    mock_db.__getitem__.assert_called_once_with('process_history')
    mock_db.__getitem__.return_value.insert.assert_called_once()
    args, kwargs = mock_db.__getitem__.return_value.insert.call_args
    assert kwargs['pid'] == 123
    assert kwargs['name'] == "test_process"

@patch('src.backendbot.refactored_modules.utils.db')
def test_store_optimization_event(mock_db):
    store_optimization_event(250.75)
    mock_db.__getitem__.assert_called_once_with('optimization_events')
    mock_db.__getitem__.return_value.insert.assert_called_once()
    args, kwargs = mock_db.__getitem__.return_value.insert.call_args
    assert kwargs['freed_ram_mb'] == 250.75

@patch('src.backendbot.refactored_modules.utils.db')
def test_store_watchdog_decision(mock_db):
    store_watchdog_decision("test_program", "suspended", 10.0, 200.0)
    mock_db.__getitem__.assert_called_once_with('watchdog_decisions')
    mock_db.__getitem__.return_value.insert.assert_called_once()
    args, kwargs = mock_db.__getitem__.return_value.insert.call_args
    assert kwargs['program_name'] == "test_program"
    assert kwargs['action'] == "suspended"

@patch('src.backendbot.refactored_modules.utils.settings', Settings())
@patch('psutil.process_iter')
@patch('subprocess.Popen')
@patch('src.backendbot.refactored_modules.utils.log_event')
def test_restore_closed_processes(mock_log_event, mock_popen, mock_process_iter):
    # Simulate some processes running and some not
    mock_process_iter.return_value = [
        MagicMock(info={'name': 'explorer.exe'}),
        MagicMock(info={'name': 'chrome.exe'})
    ]
    
    # Mock PROCESOS_IMPORTANTES to include one that is running and one that is not
    with patch.object(Settings, 'PROCESOS_IMPORTANTES', ["explorer.exe", "DaVinci Resolve.exe"]):
        restore_closed_processes("some_mode")
        
        # explorer.exe is running, so Popen should not be called for it
        # DaVinci Resolve.exe is not running, so Popen should be called for it
        mock_popen.assert_called_once_with("DaVinci Resolve.exe")
        mock_log_event.assert_called_once_with("Proceso restaurado: DaVinci Resolve.exe")
