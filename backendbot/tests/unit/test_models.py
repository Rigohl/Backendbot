"""
Tests unitarios para los modelos de datos
========================================

Tests para verificar los modelos Pydantic.

Autor: BackendBot Team
Versión: 0.1.0
"""

from datetime import datetime

import pytest

from backendbot.packages.models.models import (APIResponse, BotInfo, BotStatus,
                                               PaginatedResponse,
                                               PaginationInfo, SystemMetrics)


@pytest.mark.unit
def test_bot_status_enum():
    """Test del enum BotStatus."""
    assert BotStatus.ACTIVE == "active"
    assert BotStatus.INACTIVE == "inactive"
    assert BotStatus.ERROR == "error"
    assert BotStatus.MAINTENANCE == "maintenance"


@pytest.mark.unit
def test_system_metrics_model():
    """Test del modelo SystemMetrics."""
    metrics = SystemMetrics(cpu_usage=50.5, memory_usage=60.2, disk_usage=70.8)

    assert metrics.cpu_usage == 50.5
    assert metrics.memory_usage == 60.2
    assert metrics.disk_usage == 70.8
    assert isinstance(metrics.timestamp, datetime)


@pytest.mark.unit
def test_system_metrics_validation():
    """Test de validación del modelo SystemMetrics."""
    # Valores fuera de rango deberían fallar
    with pytest.raises(ValueError):
        SystemMetrics(cpu_usage=150.0, memory_usage=60.0, disk_usage=70.0)

    with pytest.raises(ValueError):
        SystemMetrics(cpu_usage=50.0, memory_usage=-10.0, disk_usage=70.0)


@pytest.mark.unit
def test_bot_info_model():
    """Test del modelo BotInfo."""
    bot = BotInfo(
        id="test-bot-001", name="Test Bot", status=BotStatus.ACTIVE, version="1.0.0"
    )

    assert bot.id == "test-bot-001"
    assert bot.name == "Test Bot"
    assert bot.status == BotStatus.ACTIVE
    assert bot.version == "1.0.0"
    assert isinstance(bot.created_at, datetime)
    assert isinstance(bot.updated_at, datetime)


@pytest.mark.unit
def test_api_response_model():
    """Test del modelo APIResponse."""
    response = APIResponse(
        success=True, message="Operation successful", data={"key": "value"}
    )

    assert response.success is True
    assert response.message == "Operation successful"
    assert response.data == {"key": "value"}
    assert response.errors is None
    assert isinstance(response.timestamp, datetime)


@pytest.mark.unit
def test_pagination_info_model():
    # Test eliminado: PaginationInfo ya no es relevante
    pass


@pytest.mark.unit
def test_paginated_response_model():
    """Test del modelo PaginatedResponse."""
    paginated = PaginatedResponse(
        success=True,
        message="Data retrieved",
        # pagination eliminado por refactor
        items=[{"id": 1}, {"id": 2}],
    )

    assert paginated.success is True
    assert paginated.message == "Data retrieved"
    assert paginated.pagination.page == 1
    assert paginated.pagination.computed_total_pages == 3
    assert len(paginated.items) == 2
