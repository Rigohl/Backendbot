import os
import sys
import pytest
from unittest.mock import patch, MagicMock
import time
import psutil

# Agregar src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backendbot.watchdog import watchdog, _handle_process_monitoring
from backendbot.config import Settings

# Mock settings for watchdog
@patch('backendbot.watchdog.settings', Settings())
@patch('backendbot.watchdog.log_event')
@patch('backendbot.watchdog.notify')
@patch('backendbot.watchdog.store_watchdog_decision')
@pytest.mark.asyncio
async def test_handle_process_monitoring_high_usage_notify(mock_store_decision, mock_notify, mock_log_event):
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
        await _handle_process_monitoring(mock_process, uso_alto, memory)
        # First check, just adds to uso_alto
        assert uso_alto[123] == 100

    with patch('time.time', return_value=100 + Settings().CHECK_TIME + 1):
        await _handle_process_monitoring(mock_process, uso_alto, memory)
        # Should notify due to high usage over time
        mock_notify.assert_called_once_with("⚠️ test_process alto consumo. Revisa dashboard.", subtle=True)
        mock_store_decision.assert_called_once_with("test_process", "notificado", 90.0, 5000.0)
        assert 123 not in uso_alto # Should be removed after action

@patch('backendbot.watchdog.settings', Settings())
@patch('backendbot.watchdog.log_event')
@patch('backendbot.watchdog.notify')
@patch('backendbot.watchdog.store_watchdog_decision')
@pytest.mark.asyncio
async def test_handle_process_monitoring_suspend(mock_store_decision, mock_notify, mock_log_event):
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
        await _handle_process_monitoring(mock_process, uso_alto, memory)

    with patch('time.time', return_value=100 + Settings().CHECK_TIME + 1):
        await _handle_process_monitoring(mock_process, uso_alto, memory)
        mock_process.suspend.assert_called_once()
        mock_notify.assert_called_once_with("🔄 test_process suspendido automáticamente")
        mock_store_decision.assert_called_once_with("test_process", "suspendido", 90.0, 5000.0)
        assert 123 not in uso_alto

@patch('backendbot.watchdog.settings', Settings())
@patch('backendbot.watchdog.log_event')
@patch('backendbot.watchdog.notify')
@patch('backendbot.watchdog.store_watchdog_decision')
@pytest.mark.asyncio
async def test_handle_process_monitoring_ignored(mock_store_decision, mock_notify, mock_log_event):
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
        await _handle_process_monitoring(mock_process, uso_alto, memory)

    with patch('time.time', return_value=100 + Settings().CHECK_TIME + 1):
        await _handle_process_monitoring(mock_process, uso_alto, memory)
        mock_log_event.assert_called_once_with("test_process ignorado")
        mock_store_decision.assert_called_once_with("test_process", "ignorado", 90.0, 5000.0)
        assert 123 not in uso_alto

@patch('backendbot.watchdog.settings', Settings())
@patch('backendbot.watchdog.log_event')
@patch('backendbot.watchdog.notify')
@patch('backendbot.watchdog.store_watchdog_decision')
@patch('backendbot.watchdog.load_memory', return_value={})
@patch('psutil.process_iter')
@pytest.mark.asyncio
async def test_watchdog_main_loop(mock_process_iter, mock_load_memory, mock_store_decision, mock_notify, mock_log_event):
    # Simulate one iteration of the watchdog loop
    mock_process_iter.return_value = [
        MagicMock(info={'pid': 1, 'name': 'idle', 'cpu_percent': 5.0, 'memory_info': MagicMock(rss=100*1024*1024)}),
        MagicMock(info={'pid': 2, 'name': 'high_cpu', 'cpu_percent': 90.0, 'memory_info': MagicMock(rss=200*1024*1024)})
    ]

    # To stop the infinite loop for testing, we'll patch asyncio.sleep to raise an exception
    with patch('asyncio.sleep', side_effect=Exception("StopLoop")):
        with pytest.raises(Exception, match="StopLoop"):
            await watchdog()

    # Verify that _handle_process_monitoring was called for each process
    assert mock_process_iter.call_count == 1
    # The specific assertions for _handle_process_monitoring are covered by its own tests

@patch('backendbot.watchdog.settings', Settings())
@patch('backendbot.watchdog.log_event')
@patch('backendbot.watchdog.notify')
@patch('backendbot.watchdog.store_watchdog_decision')
@patch('backendbot.watchdog.load_memory', return_value={})
@patch('psutil.process_iter', side_effect=Exception("ProcessIterError"))
@pytest.mark.asyncio
async def test_watchdog_main_loop_error_handling(mock_process_iter, mock_load_memory, mock_store_decision, mock_notify, mock_log_event):
    # To stop the infinite loop for testing, we'll patch asyncio.sleep to raise an exception
    with patch('asyncio.sleep', side_effect=Exception("StopLoop")):
        with pytest.raises(Exception, match="StopLoop"):
            await watchdog()

    mock_log_event.assert_called_once_with("Error en watchdog principal: ProcessIterError")

# Ejemplo de test básico para Settings

def test_watchdog_settings():
    s = Settings()
    assert isinstance(s.HIBERNABLES, list)
    assert isinstance(s.PROCESOS_A_CERRAR, dict)
    assert isinstance(s.PROCESOS_IMPORTANTES, list)
