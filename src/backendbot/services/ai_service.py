import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import logging

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload # For eager loading relationships

from ..config import settings
from ..utils import log_event
from ..database import AIConversation as DBConversation, AIMessage as DBMessage
from fastapi import HTTPException

logger = logging.getLogger(__name__)


@dataclass
class AIMessage:
    """Mensaje de IA para manejo en memoria"""
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata_: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata_
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIMessage':
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata_=data.get("metadata")
        )


@dataclass
class AIConversation:
    """Conversación de IA para manejo en memoria"""
    id: str
    model: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    context: Optional[Dict[str, Any]] = None
    messages: List[AIMessage] = field(default_factory=list)

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Agrega un mensaje a la conversación"""
        message = AIMessage(role=role, content=content, metadata_=metadata)
        self.messages.append(message)
        self.updated_at = datetime.now()

    def get_messages_for_api(self) -> List[Dict[str, Any]]:
        """Obtiene los mensajes en formato para API"""
        return [msg.to_dict() for msg in self.messages]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "model": self.model,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "context": self.context,
            "messages": [msg.to_dict() for msg in self.messages]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIConversation':
        return cls(
            id=data["id"],
            model=data["model"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            context=data.get("context"),
            messages=[AIMessage.from_dict(msg) for msg in data.get("messages", [])]
        )


# AIConversation is imported from database module


class OllamaClient:
    """Cliente para interactuar con Ollama API"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self._session: Optional[aiohttp.ClientSession] = None # Renamed to _session

    async def _get_session(self) -> aiohttp.ClientSession:
        """Lazily create and return the aiohttp client session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close_session(self):
        """Explicitly close the aiohttp client session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    

    async def check_connection(self) -> bool:
        """Verifica si Ollama está disponible"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags") as response:
                return response.status == 200
        except Exception as e:
            log_event(f"Error conectando con Ollama: {e}")
            return False

    async def list_models(self) -> List[Dict[str, Any]]:
        """Lista los modelos disponibles en Ollama"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags") as response:
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
            session = await self._get_session()
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                **kwargs
            }

            async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
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
            session = await self._get_session()
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                **kwargs
            }

            async with session.post(f"{self.base_url}/api/chat", json=payload) as response:
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

        async with AsyncSessionLocal() as session:
            new_conversation = AIConversation(
                id=conversation_id,
                model=model,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                context={"model": model}
            )
            session.add(new_conversation)
            await session.commit()
            await session.refresh(new_conversation)

            if system_prompt:
                new_message = AIMessage(
                    conversation_id=conversation_id,
                    role="system",
                    content=system_prompt,
                    timestamp=datetime.now(),
                    metadata_={'type': 'system_prompt'}
                )
                session.add(new_message)
                await session.commit()

        return conversation_id

    async def send_message(self, conversation_id: str, message: str, **kwargs) -> Optional[str]:
        """Envía un mensaje en una conversación"""
        async with AsyncSessionLocal() as session:
            # Load conversation with messages
            stmt = select(AIConversation).options(selectinload(AIConversation.messages)).where(AIConversation.id == conversation_id)
            result = await session.execute(stmt)
            conversation = result.scalars().first()

            if not conversation:
                return None

            # Add user message
            user_message = AIMessage(
                conversation_id=conversation_id,
                role="user",
                content=message,
                timestamp=datetime.now(),
                metadata_={'type': 'user_input'}
            )
            session.add(user_message)
            await session.commit()
            await session.refresh(user_message)

            # Prepare messages for Ollama
            ollama_messages = []
            for msg in conversation.messages:
                ollama_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            ollama_messages.append({"role": user_message.role, "content": user_message.content}) # Add the new user message

            # Generate response
            async with self.ollama as client:
                response_content = await client.chat(conversation.model, ollama_messages, **kwargs)

            if response_content:
                # Add assistant response
                assistant_message = AIMessage(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=response_content,
                    timestamp=datetime.now(),
                    metadata_={'type': 'ai_response', 'model': conversation.model}
                )
                session.add(assistant_message)
                conversation.updated_at = datetime.now()
                await session.commit()
                await session.refresh(assistant_message)

            return response_content

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
        async with AsyncSessionLocal() as session:
            stmt = select(AIAgent).where(AIAgent.name == name)
            result = await session.execute(stmt)
            existing_agent = result.scalars().first()

            if existing_agent:
                return False

            new_agent = AIAgent(
                name=name,
                description=description,
                capabilities=capabilities, # Stored as JSON
                model=model,
                created_at=datetime.now(),
                system_prompt=f"Eres {name}, un agente especializado en: {', '.join(capabilities)}. {description}",
            )
            session.add(new_agent)
            await session.commit()
            await session.refresh(new_agent)
            return True

    async def execute_agent_task(self, agent_name: str, task: str) -> Optional[str]:
        """Ejecuta una tarea usando un agente específico"""
        async with AsyncSessionLocal() as session:
            stmt = select(AIAgent).where(AIAgent.name == agent_name)
            result = await session.execute(stmt)
            agent = result.scalars().first()

            if not agent:
                return None

            # Create temporary conversation for the agent
            conversation_id = await self.create_conversation(agent.model, agent.system_prompt)

            # Execute task
            result = await self.send_message(conversation_id, task)

            # Link conversation to agent (if not already linked)
            # This part needs careful consideration if agent.conversations is a relationship
            # For now, assuming it's a simple list of IDs in the agent model
            # If agent.conversations is a JSON field, update it
            if conversation_id not in agent.capabilities: # Assuming capabilities is where conversation IDs are stored for now
                agent.capabilities.append(conversation_id) # This is a temporary hack, needs proper relationship
                await session.commit()

            return result

    async def list_ai_conversations(self):
        """Lista todas las conversaciones de IA"""
        async with AsyncSessionLocal() as session:
            stmt = select(AIConversation).options(selectinload(AIConversation.messages))
            result = await session.execute(stmt)
            conversations = result.scalars().all()

            return {"conversations": [
                {
                    "id": conv.id,
                    "model": conv.model,
                    "message_count": len(conv.messages),
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "last_message": conv.messages[-1].content[:100] + "..." if conv.messages else None
                } for conv in conversations
            ]}

    async def get_ai_conversation(self, conversation_id: str):
        """Obtiene los detalles de una conversación específica"""
        async with AsyncSessionLocal() as session:
            stmt = select(AIConversation).options(selectinload(AIConversation.messages)).where(AIConversation.id == conversation_id)
            result = await session.execute(stmt)
            conversation = result.scalars().first()

            if not conversation:
                raise HTTPException(status_code=404, detail="Conversación no encontrada")

            messages_data = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata_
                } for msg in conversation.messages
            ]

            return {
                "id": conversation.id,
                "model": conversation.model,
                "messages": messages_data,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
                "context": conversation.context
            }

    async def list_ai_agents(self):
        """Lista todos los agentes de IA disponibles"""
        async with AsyncSessionLocal() as session:
            stmt = select(AIAgent)
            result = await session.execute(stmt)
            agents = result.scalars().all()

            return {"agents": [
                {
                    "name": agent.name,
                    "description": agent.description,
                    "capabilities": agent.capabilities,
                    "model": agent.model,
                    "created_at": agent.created_at.isoformat(),
                    "system_prompt": agent.system_prompt # Include system_prompt for agent details
                } for agent in agents
            ]}

    async def delete_ai_conversation(self, conversation_id: str):
        """Elimina una conversación de IA"""
        async with AsyncSessionLocal() as session:
            stmt = delete(AIConversation).where(AIConversation.id == conversation_id)
            result = await session.execute(stmt)
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Conversación no encontrada")
            await session.commit()
            return {"deleted": True, "conversation_id": conversation_id}

    async def delete_ai_agent(self, agent_name: str):
        """Elimina un agente de IA"""
        async with AsyncSessionLocal() as session:
            stmt = delete(AIAgent).where(AIAgent.name == agent_name)
            result = await session.execute(stmt)
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Agente no encontrado")
            await session.commit()
            return {"deleted": True, "agent_name": agent_name}

    def _load_conversations(self):
        """Carga las conversaciones desde el archivo JSON"""
        try:
            conversations_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "ai_conversations.json")
            if os.path.exists(conversations_file):
                with open(conversations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for conv_data in data.get("conversations", []):
                        conversation = AIConversation.from_dict(conv_data)
                        self.conversations[conversation.id] = conversation
        except Exception as e:
            log_event(f"Error cargando conversaciones: {e}")

    def _load_agents(self):
        """Carga los agentes desde el archivo JSON"""
        try:
            agents_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "ai_agents.json")
            if os.path.exists(agents_file):
                with open(agents_file, 'r', encoding='utf-8') as f:
                    self.agents = json.load(f)
        except Exception as e:
            log_event(f"Error cargando agentes: {e}")

    async def _save_conversations(self):
        """Guarda las conversaciones en el archivo JSON"""
        try:
            conversations_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "ai_conversations.json")
            os.makedirs(os.path.dirname(conversations_file), exist_ok=True)

            data = {
                "conversations": [conv.to_dict() for conv in self.conversations.values()]
            }

            with open(conversations_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_event(f"Error guardando conversaciones: {e}")

    async def _save_agents(self):
        """Guarda los agentes en el archivo JSON"""
        try:
            agents_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "ai_agents.json")
            os.makedirs(os.path.dirname(agents_file), exist_ok=True)

            with open(agents_file, 'w', encoding='utf-8') as f:
                json.dump(self.agents, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_event(f"Error guardando agentes: {e}")

    async def create_agent(self, name: str, role: str, capabilities: List[str]) -> bool:
        """Crea un nuevo agente de IA"""
        try:
            if name in self.agents:
                return False

            self.agents[name] = {
                "role": role,
                "capabilities": capabilities,
                "created_at": datetime.now().isoformat(),
                "conversation_id": None
            }

            await self._save_agents()
            return True
        except Exception as e:
            log_event(f"Error creando agente {name}: {e}")
            return False

    async def execute_agent_task(self, agent_name: str, task: str) -> Optional[str]:
        """Ejecuta una tarea usando un agente específico"""
        try:
            if agent_name not in self.agents:
                return None

            agent = self.agents[agent_name]
            conversation_id = agent.get("conversation_id")

            if not conversation_id:
                # Crear nueva conversación para el agente
                conversation_id = await self.create_conversation("llama2:7b")
                agent["conversation_id"] = conversation_id
                await self._save_agents()

            # Ejecutar la tarea
            return await self.send_message(conversation_id, f"Como {agent['role']}, {task}")
        except Exception as e:
            log_event(f"Error ejecutando tarea del agente {agent_name}: {e}")
            return None

    async def analyze_system_status(self) -> Dict[str, Any]:
        """Analiza el estado del sistema usando IA"""
        try:
            # Obtener información del sistema
            import psutil
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            analysis_prompt = f"""
            Analiza el siguiente estado del sistema y proporciona recomendaciones:

            CPU: {cpu_usage}%
            Memoria: {memory.percent}% usado ({memory.used/1024/1024/1024:.1f}GB de {memory.total/1024/1024/1024:.1f}GB)
            Disco: {disk.percent}% usado ({disk.used/1024/1024/1024:.1f}GB de {disk.total/1024/1024/1024:.1f}GB)

            Proporciona un análisis breve y recomendaciones específicas.
            """

            # Crear conversación temporal para el análisis
            conversation_id = await self.create_conversation("llama2:7b")
            response = await self.send_message(conversation_id, analysis_prompt)

            return {
                "analysis": response or "No se pudo generar el análisis",
                "system_info": {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory.percent,
                    "disk_usage": disk.percent,
                    "memory_total_gb": memory.total/1024/1024/1024,
                    "memory_used_gb": memory.used/1024/1024/1024,
                    "disk_total_gb": disk.total/1024/1024/1024,
                    "disk_used_gb": disk.used/1024/1024/1024
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            log_event(f"Error analizando estado del sistema: {e}")
            return {
                "analysis": "Error al analizar el sistema",
                "system_info": {},
                "timestamp": datetime.now().isoformat()
            }

# Instancia global del servicio de IA
ai_service = AIService()

# Capacidades disponibles para agentes de IA
AI_AGENT_CAPABILITIES = [
    "system_analysis",
    "process_optimization",
    "memory_management",
    "performance_monitoring",
    "troubleshooting",
    "automation_suggestions",
    "resource_prediction",
    "security_analysis"
]

# Instancia global del servicio de IA
ai_service = AIService()