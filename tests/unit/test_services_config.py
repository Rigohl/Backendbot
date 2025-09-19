from backendbot.services.config_service import ConfigService


def test_config_service_basic():
    svc = ConfigService()
    # Llamar get para una clave posible, no debe lanzar
    val = svc.get('environment', 'dev')
    assert val is not None
