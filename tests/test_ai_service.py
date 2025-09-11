import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from src.backendbot.services.ai_service import (
    OllamaClient,
    AIMessage,
    AIConversation,
    AIService,
    AI_AGENT_CAPABILITIES
)


class TestOllamaClient:
    """Tests para el cliente de Ollama"""

    @pytest.fixture
    def client(self):
        return OllamaClient(base_url="http://localhost:11434")

    @pytest.mark.asyncio
    async def test_check_status_success(self, client):
        """Test de verificación de estado exitoso"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"version": "0.1.0"})
            mock_get.return_value.__aenter__.return_value = mock_response

            status = await client.check_connection()
            assert status["available"] is True
            assert status["version"] == "0.1.0"

    @pytest.mark.asyncio
    async def test_check_status_failure(self, client):
        """Test de verificación de estado fallido"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("Connection failed")

            status = await client.check_connection()
            assert status["available"] is False
            assert "error" in status

    @pytest.mark.asyncio
    async def test_list_models_success(self, client):
        """Test de listado de modelos exitoso"""
        mock_models = {
            "models": [
                {"name": "llama2:7b", "size": 1000000},
                {"name": "codellama:7b", "size": 2000000}
            ]
        }

        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_models)
            mock_get.return_value.__aenter__.return_value = mock_response

            models = await client.list_models()
            assert len(models) == 2
            assert models[0]["name"] == "llama2:7b"

    @pytest.mark.asyncio
    async def test_generate_response_success(self, client):
        """Test de generación de respuesta exitosa"""
        mock_response_data = {
            "response": "Hello, this is a test response",
            "done": True,
            "context": [1, 2, 3, 4]
        }

        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_post.return_value.__aenter__.return_value = mock_response

            response = await client.generate(
                model="llama2:7b",
                prompt="Hello",
                context=[1, 2, 3]
            )

            assert response["response"] == "Hello, this is a test response"
            assert response["done"] is True


class TestAIMessage:
    """Tests para la clase AIMessage"""

    def test_message_creation(self):
        """Test de creación de mensaje"""
        from datetime import datetime
        message = AIMessage(
            role="user",
            content="Hello AI",
            timestamp=datetime.now(),
            metadata={"temperature": 0.7}
        )

        assert message.role == "user"
        assert message.content == "Hello AI"
        assert message.metadata["temperature"] == 0.7
        assert isinstance(message.timestamp, datetime)

    def test_message_to_dict(self):
        """Test de conversión a diccionario"""
        from datetime import datetime
        message = AIMessage(role="assistant", content="Hello human", timestamp=datetime.now())
        msg_dict = message.to_dict()

        assert msg_dict["role"] == "assistant"
        assert msg_dict["content"] == "Hello human"
        assert "timestamp" in msg_dict

    def test_message_from_dict(self):
        """Test de creación desde diccionario"""
        from datetime import datetime
        msg_dict = {
            "role": "user",
            "content": "Test message",
            "timestamp": datetime.now(),
            "metadata": {"test": True}
        }

        message = AIMessage(**msg_dict)
        assert message.role == "user"
        assert message.content == "Test message"
        assert message.metadata["test"] is True


class TestAIConversation:
    """Tests para la clase AIConversation"""

    def test_conversation_creation(self):
        """Test de creación de conversación"""
        from datetime import datetime
        conversation = AIConversation(
            id="test_conv",
            messages=[],
            model="llama2:7b",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        assert conversation.id is not None
        assert conversation.model == "llama2:7b"
        assert len(conversation.messages) == 0
        assert isinstance(conversation.created_at, datetime)

    def test_add_message(self):
        """Test de agregar mensaje"""
        from datetime import datetime
        conversation = AIConversation(
            id="test_conv",
            messages=[],
            model="llama2:7b",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        message = AIMessage(role="user", content="Hello")

        conversation.add_message(message)

        assert len(conversation.messages) == 1
        assert conversation.messages[0].content == "Hello"
        assert conversation.updated_at > conversation.created_at

    def test_get_messages_for_api(self):
        """Test de obtener mensajes para API"""
        from datetime import datetime
        conversation = AIConversation(
            id="test_conv",
            messages=[],
            model="llama2:7b",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        conversation.add_message(AIMessage(role="user", content="Hello"))
        conversation.add_message(AIMessage(role="assistant", content="Hi there"))

        messages = conversation.get_messages_for_api()

        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"

    def test_to_dict_and_from_dict(self):
        """Test de serialización"""
        from datetime import datetime
        conversation = AIConversation(
            id="test_conv",
            messages=[],
            model="llama2:7b",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        conversation.add_message(AIMessage(role="user", content="Test"))

        conv_dict = conversation.to_dict()
        restored = AIConversation.from_dict(conv_dict)

        assert restored.id == conversation.id
        assert restored.model == conversation.model
        assert len(restored.messages) == 1


class TestAIService:
    """Tests para el servicio de IA"""

    @pytest.fixture
    def ai_service(self):
        with patch('src.backendbot.services.ai_service.OllamaClient'):
            service = AIService()
            return service

    @pytest.mark.asyncio
    async def test_check_ollama_status(self, ai_service):
        """Test de verificación de estado de Ollama"""
        with patch.object(ai_service.ollama, 'check_connection', return_value=True) as mock_check:
            with patch.object(ai_service.ollama, 'list_models', return_value=[{"name": "llama2"}]) as mock_list:
                status = await ai_service.check_ollama_status()
                assert status["connected"] is True
                assert len(status["models"]) == 1

    @pytest.mark.asyncio
    async def test_create_conversation(self, ai_service):
        """Test de creación de conversación"""
        conversation_id = await ai_service.create_conversation("llama2:7b", "You are helpful")

        assert conversation_id in ai_service.conversations
        conv = ai_service.conversations[conversation_id]
        assert conv.model == "llama2:7b"
        assert len(conv.messages) == 1  # System message

    @pytest.mark.asyncio
    async def test_send_message(self, ai_service):
        """Test de envío de mensaje"""
        conversation_id = await ai_service.create_conversation("llama2:7b")

        mock_response = {
            "response": "Hello! How can I help you?",
            "done": True,
            "context": [1, 2, 3]
        }

        with patch.object(ai_service.ollama, 'chat', return_value="Hello! How can I help you?") as mock_chat:
            response = await ai_service.send_message(conversation_id, "Hello")

            assert response == "Hello! How can I help you?"
            conv = ai_service.conversations[conversation_id]
            assert len(conv.messages) == 3  # System + user + assistant

    @pytest.mark.asyncio
    async def test_send_message_conversation_not_found(self, ai_service):
        """Test de envío de mensaje con conversación inexistente"""
        response = await ai_service.send_message("nonexistent", "Hello")
        assert response is None

    @pytest.mark.asyncio
    async def test_analyze_system_status(self, ai_service):
        """Test de análisis del sistema"""
        with patch.object(ai_service.ollama, 'generate') as mock_generate:
            mock_generate.return_value = "System analysis complete"

            analysis = await ai_service.analyze_system_status()
            assert "analysis" in analysis
            assert "recommendations" in analysis

    @pytest.mark.asyncio
    async def test_create_agent(self, ai_service):
        """Test de creación de agente"""
        success = await ai_service.create_agent(
            "test_agent",
            "Test agent",
            ["chat", "analyze"],
            "llama2:7b"
        )

        assert success is True
        assert "test_agent" in ai_service.agents
        agent = ai_service.agents["test_agent"]
        assert agent["description"] == "Test agent"
        assert "chat" in agent["capabilities"]

    @pytest.mark.asyncio
    async def test_create_agent_duplicate(self, ai_service):
        """Test de creación de agente duplicado"""
        await ai_service.create_agent("test_agent", "Test", ["chat"], "llama2:7b")
        success = await ai_service.create_agent("test_agent", "Test", ["chat"], "llama2:7b")
        assert success is False

    @pytest.mark.asyncio
    async def test_execute_agent_task(self, ai_service):
        """Test de ejecución de tarea de agente"""
        await ai_service.create_agent("test_agent", "Test", ["chat"], "llama2:7b")

        with patch.object(ai_service.ollama, 'chat') as mock_chat:
            mock_chat.return_value = "Task completed"

            result = await ai_service.execute_agent_task("test_agent", "Analyze data")
            assert result is not None
            assert result == "Task completed"

    @pytest.mark.asyncio
    async def test_execute_agent_task_not_found(self, ai_service):
        """Test de ejecución de tarea con agente inexistente"""
        result = await ai_service.execute_agent_task("nonexistent", "Task")
        assert result is None


class TestAIIntegration:
    """Tests de integración para el sistema de IA"""

    @pytest.mark.asyncio
    async def test_full_conversation_flow(self):
        """Test de flujo completo de conversación"""
        with patch('src.backendbot.services.ai_service.OllamaClient'):
            service = AIService()

            # Crear conversación
            conv_id = await service.create_conversation("llama2:7b", "You are a helpful assistant")

            # Mock respuesta de Ollama
            with patch.object(service.ollama, 'chat') as mock_chat:
                mock_chat.return_value = "Hello! I'm here to help."

                # Enviar mensaje
                response = await service.send_message(conv_id, "Hello AI")

                assert response == "Hello! I'm here to help."
                conv = service.conversations[conv_id]
                assert len(conv.messages) == 3  # system + user + assistant

    @pytest.mark.asyncio
    async def test_agent_workflow(self):
        """Test de flujo de trabajo de agente"""
        with patch('src.backendbot.services.ai_service.OllamaClient'):
            service = AIService()

            # Crear agente
            await service.create_agent(
                "analyzer",
                "Data analyzer",
                ["analyze", "chat"],
                "llama2:7b"
            )

            # Mock respuesta para tarea
            with patch.object(service.ollama, 'chat') as mock_chat:
                mock_chat.return_value = "Analysis complete: Data looks good"

                # Ejecutar tarea
                result = await service.execute_agent_task("analyzer", "Analyze this data: [1,2,3,4,5]")

                assert result is not None
                assert result == "Analysis complete: Data looks good"

                # Verificar que se guardó la conversación del agente
                agent = service.agents["analyzer"]
                assert len(agent["conversations"]) == 1


if __name__ == "__main__":
    pytest.main([__file__])