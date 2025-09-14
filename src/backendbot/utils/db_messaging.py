from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import Session
from src.backendbot.utils.db import Base, SessionLocal, engine
import json
import time

# --- Modelos de Tablas de Mensajería ---

class CommandQueue(Base):
    __tablename__ = "command_queue"
    id = Column(Integer, primary_key=True, index=True)
    bot_name = Column(String, index=True) # A qué bot va dirigido el comando
    command_type = Column(String) # Tipo de comando (ej. "scan_duplicates", "start_indexing")
    payload = Column(Text) # Datos del comando en JSON
    created_at = Column(DateTime, default=func.now())
    status = Column(String, default="pending") # pending, processing, completed, failed
    processed_by = Column(String, nullable=True) # Nombre del bot que lo procesa

class ResultQueue(Base):
    __tablename__ = "result_queue"
    id = Column(Integer, primary_key=True, index=True)
    bot_name = Column(String, index=True)
    result_type = Column(String) # Tipo de resultado (ej. "scan_duplicates_result", "indexed_files_count")
    payload = Column(Text) # Datos del resultado en JSON
    created_at = Column(DateTime, default=func.now())
    consumed = Column(DateTime, nullable=True) # Cuando fue consumido por el Orquestador

class BotState(Base):
    __tablename__ = "bot_state"
    id = Column(Integer, primary_key=True, index=True)
    bot_name = Column(String, unique=True, index=True)
    state_key = Column(String, unique=True, index=True) # Clave del estado (ej. "system_stats_latest")
    state_value = Column(Text) # Valor del estado en JSON
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())

# --- Funciones de Interacción con la DB para Mensajería ---

def create_messaging_tables():
    Base.metadata.create_all(bind=engine)

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Comandos
def send_command(bot_name: str, command_type: str, payload: dict):
    try:
        db = next(get_db_session())
        try:
            command = CommandQueue(bot_name=bot_name, command_type=command_type, payload=json.dumps(payload))
            db.add(command)
            db.commit()
            db.refresh(command)
            return command
        finally:
            db.close()
    except Exception as e:
        print(f"Warning: Could not send command to database: {e}")
        print("This is normal if the database is not available during testing.")
        return None

def get_pending_command(bot_name: str):
    db = next(get_db_session())
    try:
        command = db.query(CommandQueue).filter(
            CommandQueue.bot_name == bot_name,
            CommandQueue.status == "pending"
        ).order_by(CommandQueue.created_at).first()
        if command:
            command.status = "processing"
            command.processed_by = bot_name # Marcar quién lo está procesando
            db.commit()
            db.refresh(command)
        return command
    finally:
        db.close()

def complete_command(command_id: int, status: str = "completed", db: Session = None):
    if db is None:
        db = next(get_db_session())
    try:
        command = db.query(CommandQueue).filter(CommandQueue.id == command_id).first()
        if command:
            command.status = status
            db.commit()
            db.refresh(command)
        return command
    finally:
        if db is not None: # Only close if session was created here
            db.close()

# Resultados
def send_result(bot_name: str, result_type: str, payload: dict):
    db = next(get_db_session())
    try:
        result = ResultQueue(bot_name=bot_name, result_type=result_type, payload=json.dumps(payload))
        db.add(result)
        db.commit()
        db.refresh(result)
        return result
    finally:
        db.close()

def get_unconsumed_results(bot_name: str = None):
    db = next(get_db_session())
    try:
        query = db.query(ResultQueue).filter(ResultQueue.consumed == None)
        if bot_name:
            query = query.filter(ResultQueue.bot_name == bot_name)
        results = query.order_by(ResultQueue.created_at).all()
        return results
    finally:
        db.close()

def mark_result_consumed(result_id: int):
    db = next(get_db_session())
    try:
        result = db.query(ResultQueue).filter(ResultQueue.id == result_id).first()
        if result:
            result.consumed = func.now()
            db.commit()
            db.refresh(result)
        return result
    finally:
        db.close()

# Estados (para datos en tiempo real como stats)
def set_bot_state(bot_name: str, state_key: str, state_value: dict):
    db = next(get_db_session())
    try:
        state = db.query(BotState).filter(BotState.bot_name == bot_name, BotState.state_key == state_key).first()
        if state:
            state.state_value = json.dumps(state_value)
        else:
            state = BotState(bot_name=bot_name, state_key=state_key, state_value=json.dumps(state_value))
            db.add(state)
        db.commit()
        db.refresh(state)
        return state
    finally:
        db.close()

def get_bot_state(bot_name: str, state_key: str):
    try:
        db = next(get_db_session())
        try:
            state = db.query(BotState).filter(BotState.bot_name == bot_name, BotState.state_key == state_key).first()
            if state:
                return json.loads(state.state_value)
            return None
        finally:
            db.close()
    except Exception as e:
        print(f"Warning: Could not connect to database in get_bot_state: {e}")
        print("This is normal if the database is not available during testing.")
        return None

# Tablas se crearán automáticamente en el lifespan del servidor
# No llamar create_messaging_tables() aquí para evitar errores de conexión
