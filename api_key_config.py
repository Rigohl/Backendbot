# BackendBot - Configuración de API Key
# =====================================
#
# Este archivo contiene la configuración para el acceso directo
# con API key a BackendBot API.
#
# Para usar el acceso directo:
# 1. Asegúrate de que BACKENDBOT_MASTER_API_KEY esté configurada en .env
# 2. Ejecuta: python api_client.py --help
# 3. O usa los ejemplos: python ejemplos_api_key.py
#
# Beneficios del acceso directo:
# - Sin necesidad de autenticación OAuth2
# - Ideal para scripts y automatización
# - Acceso rápido a todas las funcionalidades
# - Seguro con API key encriptada

# Configuración de ejemplo para scripts
API_KEY_CONFIG = {
    "api_key": None,  # Se carga automáticamente desde .env
    "base_url": "https://localhost:8443",
    "timeout": 30,
    "verify_ssl": True,
    "retry_attempts": 3,
    "retry_delay": 1.0
}

# Endpoints disponibles
ENDPOINTS = {
    "health": "/health",
    "system_status": "/system/status",
    "bots_status": "/bots/status",
    "execute_bot": "/bots/{bot_name}/execute",
    "backup_create": "/backup/create",
    "notification_send": "/notification/send",
    "power_profile": "/power/profile",
    "logs_get": "/logs",
    "config_get": "/config"
}

# Bots disponibles
BOTS = [
    "monitor",
    "organizer",
    "indexer",
    "guardian",
    "auditor_files",
    "auditor_programs"
]

# Perfiles de energía disponibles
POWER_PROFILES = [
    "high_performance",
    "balanced",
    "power_saver",
    "ultimate_performance"
]

# Canales de notificación disponibles
NOTIFICATION_CHANNELS = [
    "desktop",
    "email",
    "webhook",
    "file"
]

# Niveles de prioridad para notificaciones
NOTIFICATION_PRIORITIES = [
    "low",
    "normal",
    "high",
    "critical"
]

# Tipos de backup disponibles
BACKUP_TYPES = [
    "full",
    "incremental",
    "differential"
]

# Configuración de logging para scripts
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "api_client.log"
}

# Función helper para validar configuración
def validate_config():
    """Valida que la configuración sea correcta"""
    required_keys = ["api_key", "base_url"]
    for key in required_keys:
        if API_KEY_CONFIG.get(key) is None:
            raise ValueError(f"Configuración faltante: {key}")

    return True

# Función helper para obtener configuración completa
def get_full_config():
    """Obtiene la configuración completa con valores por defecto"""
    config = API_KEY_CONFIG.copy()

    # Cargar API key desde .env si no está configurada
    if config["api_key"] is None:
        from api_client import load_api_key_from_env
        config["api_key"] = load_api_key_from_env()

    return config