import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from ..config import settings
from ..utils import log_event

logger = logging.getLogger(__name__)

@dataclass
class AIMessage:
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AIConversation:
    id: str
    messages: List[AIMessage]
    model: str
    created_at: datetime
    updated_at: datetime
    context: Optional[Dict[str, Any]] = None

class OllamaClient:
    """Cliente para interactuar con Ollama API"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def check_connection(self) -> bool:
        """Verifica si Ollama está disponible"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.get(f"{self.base_url}/api/tags") as response:
                return response.status == 200
        except Exception as e:
            log_event(f"Error conectando con Ollama: {e}")
            return False

    async def list_models(self) -> List[Dict[str, Any]]:
        """Lista los modelos disponibles en Ollama"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("models", [])
                return []
        except Exception as e:
            log_event(f"Error listando modelos de Ollama: {e}")
            return []

    async def generate(self, model: str, prompt: str, **kwargs) -> Optional[str]:
        """Genera respuesta usando un modelo de Ollama"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                **kwargs
            }

            async with self.session.post(f"{self.base_url}/api/generate", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", "")
                return None
        except Exception as e:
            log_event(f"Error generando respuesta con Ollama: {e}")
            return None

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        """Realiza una conversación con un modelo de Ollama"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                **kwargs
            }

            async with self.session.post(f"{self.base_url}/api/chat", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("message", {}).get("content", "")
                return None
        except Exception as e:
            log_event(f"Error en chat con Ollama: {e}")
            return None

class AIService:
    """Servicio principal de IA para BackendBot"""

    def __init__(self):
        self.ollama = OllamaClient()
        self.conversations: Dict[str, AIConversation] = {}
        self.agents: Dict[str, Dict[str, Any]] = {}
        self._load_conversations()
        self._load_agents()

    def _load_conversations(self):
        """Carga conversaciones guardadas"""
        try:
            conversations_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "ai_conversations.json")
            if os.path.exists(conversations_file):
                with open(conversations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for conv_data in data.get("conversations", []):
                        messages = []
                        for msg_data in conv_data["messages"]:
                            messages.append(AIMessage(
                                role=msg_data["role"],
                                content=msg_data["content"],
                                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                                metadata=msg_data.get("metadata")
                            ))

                        conversation = AIConversation(
                            id=conv_data["id"],
                            messages=messages,
                            model=conv_data["model"],
                            created_at=datetime.fromisoformat(conv_data["created_at"]),
                            updated_at=datetime.fromisoformat(conv_data["updated_at"]),
                            context=conv_data.get("context")
                        )
                        self.conversations[conv_data["id"]] = conversation
        except Exception as e:
            log_event(f"Error cargando conversaciones de IA: {e}")

    def _save_conversations(self):
        """Guarda conversaciones"""
        try:
            conversations_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "ai_conversations.json")
            os.makedirs(os.path.dirname(conversations_file), exist_ok=True)

            data = {"conversations": []}
            for conv in self.conversations.values():
                conv_data = {
                    "id": conv.id,
                    "model": conv.model,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "context": conv.context,
                    "messages": []
                }

                for msg in conv.messages:
                    msg_data = {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                        "metadata": msg.metadata
                    }
                    conv_data["messages"].append(msg_data)

                data["conversations"].append(conv_data)

            with open(conversations_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            log_event(f"Error guardando conversaciones de IA: {e}")

    def _load_agents(self):
        """Carga configuración de agentes"""
        try:
            agents_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "ai_agents.json")
            if os.path.exists(agents_file):
                with open(agents_file, 'r', encoding='utf-8') as f:
                    self.agents = json.load(f)
        except Exception as e:
            log_event(f"Error cargando agentes de IA: {e}")

    def _save_agents(self):
        """Guarda configuración de agentes"""
        try:
            agents_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "ai_agents.json")
            os.makedirs(os.path.dirname(agents_file), exist_ok=True)

            with open(agents_file, 'w', encoding='utf-8') as f:
                json.dump(self.agents, f, indent=2, ensure_ascii=False)

        except Exception as e:
            log_event(f"Error guardando agentes de IA: {e}")

    async def check_ollama_status(self) -> Dict[str, Any]:
        """Verifica el estado de Ollama"""
        async with self.ollama as client:
            is_connected = await client.check_connection()
            models = await client.list_models() if is_connected else []

            return {
                "connected": is_connected,
                "models": models,
                "model_count": len(models)
            }

    async def create_conversation(self, model: str = "llama2", system_prompt: Optional[str] = None) -> str:
        """Crea una nueva conversación"""
        conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        messages = []
        if system_prompt:
            messages.append(AIMessage(
                role="system",
                content=system_prompt,
                timestamp=datetime.now(),
                metadata={"type": "system_prompt"}
            ))

        conversation = AIConversation(
            id=conversation_id,
            messages=messages,
            model=model,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            context={"model": model}
        )

        self.conversations[conversation_id] = conversation
        self._save_conversations()

        return conversation_id

    async def send_message(self, conversation_id: str, message: str, **kwargs) -> Optional[str]:
        """Envía un mensaje en una conversación"""
        if conversation_id not in self.conversations:
            return None

        conversation = self.conversations[conversation_id]

        # Agregar mensaje del usuario
        user_message = AIMessage(
            role="user",
            content=message,
            timestamp=datetime.now(),
            metadata={"type": "user_input"}
        )
        conversation.messages.append(user_message)

        # Preparar mensajes para Ollama
        ollama_messages = []
        for msg in conversation.messages:
            ollama_messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Generar respuesta
        async with self.ollama as client:
            response = await client.chat(conversation.model, ollama_messages, **kwargs)

        if response:
            # Agregar respuesta del asistente
            assistant_message = AIMessage(
                role="assistant",
                content=response,
                timestamp=datetime.now(),
                metadata={"type": "ai_response", "model": conversation.model}
            )
            conversation.messages.append(assistant_message)
            conversation.updated_at = datetime.now()
            self._save_conversations()

        return response

    async def analyze_system_status(self) -> Dict[str, Any]:
        """Análisis inteligente del estado del sistema usando IA"""
        system_info = {
            "cpu_usage": 0,  # TODO: Obtener de servicios existentes
            "ram_usage": 0,
            "disk_usage": 0,
            "running_processes": 0,
            "issues": []
        }

        prompt = f"""
        Analiza el siguiente estado del sistema y proporciona recomendaciones:

        CPU: {system_info['cpu_usage']}%
        RAM: {system_info['ram_usage']}%
        Disco: {system_info['disk_usage']}%
        Procesos: {system_info['running_processes']}
        Problemas detectados: {', '.join(system_info['issues']) if system_info['issues'] else 'Ninguno'}

        Proporciona:
        1. Un resumen del estado actual
        2. Problemas identificados
        3. Recomendaciones específicas
        4. Acciones prioritarias
        """

        async with self.ollama as client:
            analysis = await client.generate("llama2", prompt)

        return {
            "system_info": system_info,
            "ai_analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }

    async def create_agent(self, name: str, description: str, capabilities: List[str], model: str = "llama2") -> bool:
        """Crea un nuevo agente de IA"""
        if name in self.agents:
            return False

        agent = {
            "name": name,
            "description": description,
            "capabilities": capabilities,
            "model": model,
            "created_at": datetime.now().isoformat(),
            "system_prompt": f"Eres {name}, un agente especializado en: {', '.join(capabilities)}. {description}",
            "conversations": []
        }

        self.agents[name] = agent
        self._save_agents()
        return True

    async def execute_agent_task(self, agent_name: str, task: str) -> Optional[str]:
        """Ejecuta una tarea usando un agente específico"""
        if agent_name not in self.agents:
            return None

        agent = self.agents[agent_name]

        # Crear conversación temporal para el agente
        conversation_id = await self.create_conversation(agent["model"], agent["system_prompt"])

        # Ejecutar tarea
        result = await self.send_message(conversation_id, task)

        # Guardar referencia en el agente
        if conversation_id not in agent["conversations"]:
            agent["conversations"].append(conversation_id)
            self._save_agents()

        return result

# Instancia global del servicio de IA
ai_service = AIService()</content>
<parameter name="filePath">c:\Users\DELL\Desktop\BackendBot\src\backendbot\services\ai_service.py