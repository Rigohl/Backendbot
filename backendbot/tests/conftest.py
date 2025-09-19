"""
Configuración de pytest para BackendBot
========================================

Configuración global de pytest y fixtures compartidos.

Autor: BackendBot Team
Versión: 0.1.0
"""

import pytest


# Registro de marcas personalizadas
def pytest_configure(config):
    """Registra marcas personalizadas de pytest."""
    config.addinivalue_line("markers", "unit: Tests unitarios")
    config.addinivalue_line("markers", "integration: Tests de integración")
    config.addinivalue_line("markers", "e2e: Tests end-to-end")
    config.addinivalue_line("markers", "slow: Tests que toman tiempo")
    config.addinivalue_line("markers", "database: Tests que requieren base de datos")
    config.addinivalue_line("markers", "network: Tests que requieren conexión de red")
    config.addinivalue_line("markers", "api: Tests relacionados con la API")


@pytest.fixture(scope="session")
def backendbot_config():
    """Fixture para configuración de BackendBot."""
    from backendbot.packages.core.config import get_settings

    return get_settings()


@pytest.fixture
def sample_bot_data():
    """Fixture con datos de ejemplo para un bot."""
    return {
        "id": "test-bot-001",
        "name": "Test Bot",
        "status": "active",
        "version": "1.0.0",
        "description": "Bot de prueba para tests",
    }


@pytest.fixture
def sample_system_metrics():
    """Fixture con métricas del sistema de ejemplo."""
    return {"cpu_usage": 45.5, "memory_usage": 60.2, "disk_usage": 70.8}
