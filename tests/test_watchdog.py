import pytest
from unittest.mock import patch, MagicMock
import time
from src.backendbot.refactored_modules.watchdog import watchdog, _handle_process_monitoring
from src.backendbot.refactored_modules.config import Settings

# Mock settings for watchdog
@patch('src.backendbot.refactored_modules.watchdog.settings', Settings())
@patch('src.backendbot.refactored_modules.watchdog.log_event')
@patch('src.backendbot.refactored_modules.watchdog.notify')
@patch('src.backendbot.refactored_modules.watchdog.store_watchdog_decision')
def test_handle_process_monitoring_high_usage_notify(mock_store_decision, mock_notify, mock_log_event):
    mock_process = MagicMock()
    mock_process.info = {
        'pid': 123,
        'name': 'test_process',
        'cpu_percent': 90.0,
        'memory_info': MagicMock(rss=5000*1024*1024) # 5000 MB
    }
    mock_process.suspend.side_effect = psutil.NoSuchProcess # Simulate process disappearing

    uso_alto = {}
    memory = {'test_process': {"suspensiones": 0, "rechazos": 0}}

    with patch('time.time', return_value=100):
        _handle_process_monitoring(mock_process, uso_alto, memory)
        # First check, just adds to uso_alto
        assert uso_alto[123] == 100

    with patch('time.time', return_value=100 + Settings().CHECK_TIME + 1):
        _handle_process_monitoring(mock_process, uso_alto, memory)
        # Should notify due to high usage over time
        mock_notify.assert_called_once_with("⚠️ test_process alto consumo. Revisa dashboard.", subtle=True)
        mock_store_decision.assert_called_once_with("test_process", "notificado", 90.0, 5000.0)
        assert 123 not in uso_alto # Should be removed after action

@patch('src.backendbot.refactored_modules.watchdog.settings', Settings())
@patch('src.backendbot.refactored_modules.watchdog.log_event')
@patch('src.backendbot.refactored_modules.watchdog.notify')
@patch('src.backendbot.refactored_modules.watchdog.store_watchdog_decision')
def test_handle_process_monitoring_suspend(mock_store_decision, mock_notify, mock_log_event):
    mock_process = MagicMock()
    mock_process.info = {
        'pid': 123,
        'name': 'test_process',
        'cpu_percent': 90.0,
        'memory_info': MagicMock(rss=5000*1024*1024)
    }

    uso_alto = {}
    memory = {'test_process': {"suspensiones": 3, "rechazos": 0}}

    with patch('time.time', return_value=100):
        _handle_process_monitoring(mock_process, uso_alto, memory)

    with patch('time.time', return_value=100 + Settings().CHECK_TIME + 1):
        _handle_process_monitoring(mock_process, uso_alto, memory)
        mock_process.suspend.assert_called_once()
        mock_notify.assert_called_once_with("🔄 test_process suspendido automáticamente")
        mock_store_decision.assert_called_once_with("test_process", "suspendido", 90.0, 5000.0)
        assert 123 not in uso_alto

@patch('src.backendbot.refactored_modules.watchdog.settings', Settings())
@patch('src.backendbot.refactored_modules.watchdog.log_event')
@patch('src.backendbot.refactored_modules.watchdog.notify')
@patch('src.backendbot.refactored_modules.watchdog.store_watchdog_decision')
def test_handle_process_monitoring_ignored(mock_store_decision, mock_notify, mock_log_event):
    mock_process = MagicMock()
    mock_process.info = {
        'pid': 123,
        'name': 'test_process',
        'cpu_percent': 90.0,
        'memory_info': MagicMock(rss=5000*1024*1024)
    }

    uso_alto = {}
    memory = {'test_process': {"suspensiones": 0, "rechazos": 3}}

    with patch('time.time', return_value=100):
        _handle_process_monitoring(mock_process, uso_alto, memory)

    with patch('time.time', return_value=100 + Settings().CHECK_TIME + 1):
        _handle_process_monitoring(mock_process, uso_alto, memory)
        mock_log_event.assert_called_once_with("test_process ignorado")
        mock_store_decision.assert_called_once_with("test_process", "ignorado", 90.0, 5000.0)
        assert 123 not in uso_alto

@patch('src.backendbot.refactored_modules.watchdog.settings', Settings())
@patch('src.backendbot.refactored_modules.watchdog.log_event')
@patch('src.backendbot.refactored_modules.watchdog.notify')
@patch('src.backendbot.refactored_modules.watchdog.store_watchdog_decision')
@patch('src.backendbot.refactored_modules.watchdog.load_memory', return_value={})
@patch('psutil.process_iter')
def test_watchdog_main_loop(mock_process_iter, mock_load_memory, mock_store_decision, mock_notify, mock_log_event):
    # Simulate one iteration of the watchdog loop
    mock_process_iter.return_value = [
        MagicMock(info={'pid': 1, 'name': 'idle', 'cpu_percent': 5.0, 'memory_info': MagicMock(rss=100*1024*1024)}),
        MagicMock(info={'pid': 2, 'name': 'high_cpu', 'cpu_percent': 90.0, 'memory_info': MagicMock(rss=200*1024*1024)})
    ]

    # To stop the infinite loop for testing, we'll raise an exception after one iteration
    with patch('time.sleep', side_effect=Exception("StopLoop")):
        with pytest.raises(Exception, match="StopLoop"):
            watchdog()

    # Verify that _handle_process_monitoring was called for each process
    assert mock_process_iter.call_count == 1
    # The specific assertions for _handle_process_monitoring are covered by its own tests

@patch('src.backendbot.refactored_modules.watchdog.settings', Settings())
@patch('src.backendbot.refactored_modules.watchdog.log_event')
@patch('src.backendbot.refactored_modules.watchdog.notify')
@patch('src.backendbot.refactored_modules.watchdog.store_watchdog_decision')
@patch('src.backendbot.refactored_modules.watchdog.load_memory', return_value={})
@patch('psutil.process_iter', side_effect=Exception("ProcessIterError"))
def test_watchdog_main_loop_error_handling(mock_process_iter, mock_load_memory, mock_store_decision, mock_notify, mock_log_event):
    with patch('time.sleep', side_effect=Exception("StopLoop")):
        with pytest.raises(Exception, match="StopLoop"):
            watchdog()

    mock_log_event.assert_called_once_with("Error en watchdog principal: ProcessIterError")
