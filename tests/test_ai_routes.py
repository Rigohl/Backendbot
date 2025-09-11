import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from src.backendbot.main import app
from src.backendbot.config import settings


@pytest.fixture
def client():
    """Cliente de pruebas para FastAPI"""
    return TestClient(app)


@pytest.fixture
def mock_ai_service():
    """Mock del servicio de IA"""
    with patch('src.backendbot.api_routes.ai_service') as mock_service:
        # Configurar mocks para métodos comunes
        mock_service.check_ollama_status = AsyncMock(return_value={
            "available": True,
            "version": "0.1.0"
        })
        mock_service.create_conversation = AsyncMock(return_value="conv_123")
        mock_service.send_message = AsyncMock(return_value="AI response")
        mock_service.analyze_system_status = AsyncMock(return_value={
            "analysis": "System is healthy",
            "recommendations": ["Optimize RAM usage"]
        })
        mock_service.create_agent = AsyncMock(return_value=True)
        mock_service.execute_agent_task = AsyncMock(return_value="Task completed")
        mock_service.conversations = {}
        mock_service.agents = {}
        yield mock_service


class TestAIStatusRoutes:
    """Tests para rutas de estado de IA"""

    def test_get_ai_status_success(self, client, mock_ai_service):
        """Test de obtención de estado de IA exitoso"""
        with patch.object(settings, 'AI_ENABLED', True):
            response = client.get("/ai/status")

            assert response.status_code == 200
            data = response.json()
            assert data["ai_enabled"] is True
            assert data["ollama_status"]["available"] is True
            assert "default_model" in data

    def test_get_ai_status_ai_disabled(self, client, mock_ai_service):
        """Test de obtención de estado con IA deshabilitada"""
        with patch.object(settings, 'AI_ENABLED', False):
            response = client.get("/ai/status")

            assert response.status_code == 200
            data = response.json()
            assert data["ai_enabled"] is False


class TestAIConversationRoutes:
    """Tests para rutas de conversaciones de IA"""

    def test_create_conversation_success(self, client, mock_ai_service):
        """Test de creación de conversación exitosa"""
        with patch.object(settings, 'AI_ENABLED', True):
            response = client.post("/ai/conversation", params={
                "model": "llama2:7b",
                "system_prompt": "You are helpful"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["conversation_id"] == "conv_123"
            assert data["model"] == "llama2:7b"
            assert data["created"] is True

    def test_create_conversation_ai_disabled(self, client, mock_ai_service):
        """Test de creación de conversación con IA deshabilitada"""
        with patch.object(settings, 'AI_ENABLED', False):
            response = client.post("/ai/conversation")

            assert response.status_code == 400
            assert "deshabilitado" in response.json()["detail"]

    def test_send_message_success(self, client, mock_ai_service):
        """Test de envío de mensaje exitoso"""
        with patch.object(settings, 'AI_ENABLED', True):
            response = client.post("/ai/conversation/conv_123/message", json={
                "message": "Hello AI",
                "temperature": 0.7,
                "max_tokens": 2048
            })

            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "AI response"
            assert data["conversation_id"] == "conv_123"

    def test_send_message_ai_disabled(self, client, mock_ai_service):
        """Test de envío de mensaje con IA deshabilitada"""
        with patch.object(settings, 'AI_ENABLED', False):
            response = client.post("/ai/conversation/conv_123/message", json={
                "message": "Hello"
            })

            assert response.status_code == 400
            assert "deshabilitado" in response.json()["detail"]

    def test_list_conversations(self, client, mock_ai_service):
        """Test de listado de conversaciones"""
        # Configurar conversaciones mock
        mock_conversation = type('MockConv', (), {
            'id': 'conv_123',
            'model': 'llama2:7b',
            'messages': [type('MockMsg', (), {'content': 'Hello'})()],
            'created_at': type('MockDate', (), {'isoformat': lambda: '2024-01-01T12:00:00'})(),
            'updated_at': type('MockDate', (), {'isoformat': lambda: '2024-01-01T12:05:00'})()
        })()

        mock_ai_service.conversations = {'conv_123': mock_conversation}

        response = client.get("/ai/conversations")

        assert response.status_code == 200
        data = response.json()
        assert len(data["conversations"]) == 1
        assert data["conversations"][0]["id"] == "conv_123"

    def test_get_conversation_success(self, client, mock_ai_service):
        """Test de obtención de conversación específica"""
        # Configurar conversación mock
        mock_message = type('MockMsg', (), {
            'role': 'user',
            'content': 'Hello AI',
            'timestamp': type('MockDate', (), {'isoformat': lambda: '2024-01-01T12:00:00'})(),
            'metadata': {}
        })()

        mock_conversation = type('MockConv', (), {
            'id': 'conv_123',
            'model': 'llama2:7b',
            'messages': [mock_message],
            'created_at': type('MockDate', (), {'isoformat': lambda: '2024-01-01T12:00:00'})(),
            'updated_at': type('MockDate', (), {'isoformat': lambda: '2024-01-01T12:05:00'})(),
            'context': {}
        })()

        mock_ai_service.conversations = {'conv_123': mock_conversation}

        response = client.get("/ai/conversation/conv_123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "conv_123"
        assert len(data["messages"]) == 1

    def test_get_conversation_not_found(self, client, mock_ai_service):
        """Test de obtención de conversación inexistente"""
        response = client.get("/ai/conversation/nonexistent")

        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"]


class TestAIAnalysisRoutes:
    """Tests para rutas de análisis de IA"""

    def test_analyze_system_success(self, client, mock_ai_service):
        """Test de análisis del sistema exitoso"""
        with patch.object(settings, 'AI_ENABLED', True):
            response = client.post("/ai/analyze-system")

            assert response.status_code == 200
            data = response.json()
            assert "analysis" in data
            assert "recommendations" in data

    def test_analyze_system_ai_disabled(self, client, mock_ai_service):
        """Test de análisis del sistema con IA deshabilitada"""
        with patch.object(settings, 'AI_ENABLED', False):
            response = client.post("/ai/analyze-system")

            assert response.status_code == 400
            assert "deshabilitado" in response.json()["detail"]


class TestAIAgentRoutes:
    """Tests para rutas de agentes de IA"""

    def test_create_agent_success(self, client, mock_ai_service):
        """Test de creación de agente exitoso"""
        with patch.object(settings, 'AI_ENABLED', True):
            response = client.post("/ai/agent", json={
                "name": "test_agent",
                "description": "Test agent",
                "capabilities": ["chat", "analyze"],
                "model": "llama2:7b"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "test_agent"
            assert data["created"] is True

    def test_create_agent_ai_disabled(self, client, mock_ai_service):
        """Test de creación de agente con IA deshabilitada"""
        with patch.object(settings, 'AI_ENABLED', False):
            response = client.post("/ai/agent", json={
                "name": "test_agent",
                "description": "Test",
                "capabilities": ["chat"]
            })

            assert response.status_code == 400
            assert "deshabilitado" in response.json()["detail"]

    def test_list_agents(self, client, mock_ai_service):
        """Test de listado de agentes"""
        # Configurar agentes mock
        mock_ai_service.agents = {
            "test_agent": {
                "description": "Test agent",
                "capabilities": ["chat"],
                "model": "llama2:7b",
                "conversations": [],
                "created_at": "2024-01-01T12:00:00"
            }
        }

        response = client.get("/ai/agents")

        assert response.status_code == 200
        data = response.json()
        assert len(data["agents"]) == 1
        assert data["agents"][0]["name"] == "test_agent"

    def test_execute_agent_task_success(self, client, mock_ai_service):
        """Test de ejecución de tarea de agente exitoso"""
        with patch.object(settings, 'AI_ENABLED', True):
            response = client.post("/ai/agent/test_agent/task", json={
                "task": "Analyze data"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["agent"] == "test_agent"
            assert data["task"] == "Analyze data"
            assert data["result"] == "Task completed"

    def test_execute_agent_task_ai_disabled(self, client, mock_ai_service):
        """Test de ejecución de tarea con IA deshabilitada"""
        with patch.object(settings, 'AI_ENABLED', False):
            response = client.post("/ai/agent/test_agent/task", json={
                "task": "Analyze data"
            })

            assert response.status_code == 400
            assert "deshabilitado" in response.json()["detail"]


class TestAIDeleteRoutes:
    """Tests para rutas de eliminación de IA"""

    def test_delete_conversation_success(self, client, mock_ai_service):
        """Test de eliminación de conversación exitosa"""
        # Configurar conversación mock
        mock_conversation = type('MockConv', (), {'id': 'conv_123'})()
        mock_ai_service.conversations = {'conv_123': mock_conversation}
        mock_ai_service._save_conversations = AsyncMock()

        response = client.delete("/ai/conversation/conv_123")

        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True
        assert data["conversation_id"] == "conv_123"

    def test_delete_conversation_not_found(self, client, mock_ai_service):
        """Test de eliminación de conversación inexistente"""
        response = client.delete("/ai/conversation/nonexistent")

        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"]

    def test_delete_agent_success(self, client, mock_ai_service):
        """Test de eliminación de agente exitoso"""
        # Configurar agente mock
        mock_ai_service.agents = {"test_agent": {"description": "Test"}}
        mock_ai_service._save_agents = AsyncMock()

        response = client.delete("/ai/agent/test_agent")

        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True
        assert data["agent_name"] == "test_agent"

    def test_delete_agent_not_found(self, client, mock_ai_service):
        """Test de eliminación de agente inexistente"""
        response = client.delete("/ai/agent/nonexistent")

        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"]


class TestAIErrorHandling:
    """Tests para manejo de errores en rutas de IA"""

    def test_ai_service_exception_handling(self, client, mock_ai_service):
        """Test de manejo de excepciones del servicio de IA"""
        mock_ai_service.check_ollama_status.side_effect = Exception("Service error")

        response = client.get("/ai/status")

        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()

    def test_create_conversation_exception(self, client, mock_ai_service):
        """Test de manejo de excepciones en creación de conversación"""
        with patch.object(settings, 'AI_ENABLED', True):
            mock_ai_service.create_conversation.side_effect = Exception("Creation failed")

            response = client.post("/ai/conversation")

            assert response.status_code == 500
            assert "error" in response.json()["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__])