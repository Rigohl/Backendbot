from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import psutil

# Import the router and settings from the refactored modules
from src.backendbot.api_routes import router
from src.backendbot.refactored_modules.config import Settings

# Create a TestClient for the FastAPI app
client = TestClient(router)

# Mock the settings to use a API_KEY for testing
@patch('src.backendbot.refactored_modules.api_routes.settings', Settings(API_KEY="test-api-key"))
def test_get_api_key_valid():
    response = client.get("/procesos", headers={"api_key": "test-api-key"})
    assert response.status_code != 403 # Should not be forbidden

@patch('src.backendbot.refactored_modules.api_routes.settings', Settings(API_KEY="test-api-key"))
def test_get_api_key_invalid():
    response = client.get("/procesos", headers={"api_key": "wrong-key"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid API Key"}

@patch('src.backendbot.refactored_modules.api_routes.settings', Settings(API_KEY="test-api-key"))
@patch('psutil.process_iter')
@patch('src.backendbot.refactored_modules.api_routes.store_process_data')
def test_listar_procesos(mock_store_process_data, mock_process_iter):
    mock_process = MagicMock()
    mock_process.info = {
        'pid': 1,
        'name': 'test_proc',
        'memory_info': MagicMock(rss=100*1024*1024),
        'cpu_percent': MagicMock(return_value=10.0)
    }
    mock_process_iter.return_value = [mock_process]

    response = client.get("/procesos", headers={"api_key": "test-api-key"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "test_proc"
    mock_store_process_data.assert_called_once()

@patch('src.backendbot.refactored_modules.api_routes.settings', Settings(API_KEY="test-api-key"))
@patch('psutil.Process')
@patch('src.backendbot.refactored_modules.api_routes.log_event')
def test_apagar_proceso(mock_log_event, mock_psutil_process):
    mock_process_instance = MagicMock()
    mock_psutil_process.return_value = mock_process_instance

    response = client.post("/apagar/123", headers={"api_key": "test-api-key"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_process_instance.terminate.assert_called_once()
    mock_log_event.assert_called_once_with("Proceso terminado PID 123", notify_user=True)

@patch('src.backendbot.refactored_modules.api_routes.settings', Settings(API_KEY="test-api-key"))
@patch('psutil.Process', side_effect=psutil.NoSuchProcess)
@patch('src.backendbot.refactored_modules.api_routes.log_event')
def test_apagar_proceso_not_found(mock_log_event, mock_psutil_process):
    response = client.post("/apagar/999", headers={"api_key": "test-api-key"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Proceso PID 999 no encontrado."}

@patch('src.backendbot.refactored_modules.api_routes.settings', Settings(API_KEY="test-api-key"))
@patch('psutil.Process')
@patch('src.backendbot.refactored_modules.api_routes.log_event')
def test_resume_proceso(mock_log_event, mock_psutil_process):
    mock_process_instance = MagicMock()
    mock_psutil_process.return_value = mock_process_instance

    response = client.post("/resume/123", headers={"api_key": "test-api-key"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_process_instance.resume.assert_called_once()
    mock_log_event.assert_called_once_with("Proceso reanudado PID 123", notify_user=True)

@patch('src.backendbot.refactored_modules.api_routes.settings', Settings(API_KEY="test-api-key"))
@patch('psutil.Process')
@patch('src.backendbot.refactored_modules.api_routes.log_event')
@patch('src.backendbot.refactored_modules.api_routes.store_optimization_event')
def test_optimize(mock_store_optimization_event, mock_log_event, mock_psutil_process):
    mock_process_hibernable = MagicMock()
    mock_process_hibernable.info = {
        'pid': 1,
        'name': 'Steam.exe',
        'memory_info': MagicMock(rss=500*1024*1024) # 500 MB
    }
    mock_process_other = MagicMock()
    mock_process_other.info = {
        'pid': 2,
        'name': 'chrome.exe',
        'memory_info': MagicMock(rss=200*1024*1024)
    }
    mock_psutil_process.process_iter.return_value = [mock_process_hibernable, mock_process_other]

    response = client.post("/optimize", headers={"api_key": "test-api-key"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["ram_liberada_mb"] == 500.0
    mock_process_hibernable.suspend.assert_called_once()
    mock_process_other.suspend.assert_not_called()
    mock_log_event.assert_called_once()
    mock_store_optimization_event.assert_called_once_with(500.0)

@patch('src.backendbot.refactored_modules.api_routes.settings', Settings(API_KEY="test-api-key"))
@patch('src.backendbot.refactored_modules.api_routes.load_memory', return_value={})
@patch('src.backendbot.refactored_modules.api_routes.save_memory')
def test_guardar_decision(mock_save_memory, mock_load_memory):
    response = client.post("/decision/test_program/suspender", headers={"api_key": "test-api-key"})
    assert response.status_code == 200
    assert response.json() == {"suspensiones": 1, "rechazos": 0}
    mock_save_memory.assert_called_once()

@patch('src.backendbot.refactored_modules.api_routes.settings', Settings(API_KEY="test-api-key"))
@patch('src.backendbot.refactored_modules.api_routes.load_memory', return_value={'test_program': {"suspensiones": 5, "rechazos": 2}})
def test_ver_memoria(mock_load_memory):
    response = client.get("/memoria", headers={"api_key": "test-api-key"})
    assert response.status_code == 200
    assert response.json() == {'test_program': {"suspensiones": 5, "rechazos": 2}}

@patch('src.backendbot.refactored_modules.api_routes.settings', Settings(API_KEY="test-api-key"))
@patch('src.backendbot.refactored_modules.api_routes.save_memory')
@patch('src.backendbot.refactored_modules.api_routes.log_event')
def test_reset_memoria(mock_log_event, mock_save_memory):
    response = client.post("/reset-memoria", headers={"api_key": "test-api-key"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "msg": "Memoria reiniciada"}
    mock_save_memory.assert_called_once_with({})
    mock_log_event.assert_called_once_with("🧹 Memoria de decisiones reseteada", notify_user=True)

@patch('src.backendbot.refactored_modules.api_routes.settings', Settings(API_KEY="test-api-key"))
@patch('psutil.Process')
def test_self_metrics(mock_psutil_process):
    mock_process_instance = MagicMock()
    mock_process_instance.pid = 1234
    mock_process_instance.memory_info.return_value = MagicMock(rss=1000*1024*1024, private=500*1024*1024)
    mock_process_instance.num_threads.return_value = 5
    mock_process_instance.cpu_percent.return_value = 2.5
    mock_psutil_process.return_value = mock_process_instance

    response = client.get("/self", headers={"api_key": "test-api-key"})
    assert response.status_code == 200
    assert response.json()["pid"] == 1234
    assert response.json()["ram_mb"] == 1000.0
    assert response.json()["privados_mb"] == 500.0
    assert response.json()["num_threads"] == 5
    assert response.json()["cpu_percent"] == 2.5

@patch('src.backendbot.refactored_modules.api_routes.settings', Settings(API_KEY="test-api-key"))
@patch('src.backendbot.refactored_modules.api_routes.db')
def test_get_process_history(mock_db):
    mock_db.__getitem__.return_value.find.return_value = [{"id": 1, "name": "proc1"}]
    response = client.get("/history/processes", headers={"api_key": "test-api-key"})
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "proc1"}]

@patch('src.backendbot.refactored_modules.api_routes.settings', Settings(API_KEY="test-api-key"))
@patch('psutil.process_iter')
@patch('src.backendbot.refactored_modules.api_routes.log_event')
def test_set_modo(mock_log_event, mock_process_iter):
    mock_process_to_close = MagicMock()
    mock_process_to_close.info = {'pid': 1, 'name': 'chrome.exe'}
    mock_process_important = MagicMock()
    mock_process_important.info = {'pid': 2, 'name': 'explorer.exe'}
    mock_process_iter.return_value = [mock_process_to_close, mock_process_important]

    # Mock PROCESOS_A_CERRAR and PROCESOS_IMPORTANTES in settings
    with patch.object(Settings, 'PROCESOS_A_CERRAR', {"test_modo": ["chrome.exe"]}), \
         patch.object(Settings, 'PROCESOS_IMPORTANTES', ["explorer.exe"]):
        response = client.post("/set-modo/test_modo", headers={"api_key": "test-api-key"})
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert "chrome.exe" in response.json()["procesos_cerrados"]
        assert "explorer.exe" not in response.json()["procesos_cerrados"]
        mock_process_to_close.terminate.assert_called_once()
        mock_process_important.terminate.assert_not_called()
        mock_log_event.assert_called_once()

@patch('src.backendbot.refactored_modules.api_routes.settings', Settings(API_KEY="test-api-key"))
@patch('src.backendbot.refactored_modules.api_routes.restore_closed_processes')
def test_restore_important(mock_restore_closed_processes):
    response = client.post("/restore-important", headers={"api_key": "test-api-key"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_restore_closed_processes.assert_called_once_with(Settings().MODO)
