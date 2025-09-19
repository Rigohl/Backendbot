import pytest
from backendbot.services.logger_service import LoggerService


def test_logger_service_basic():
    svc = LoggerService('test')
    # Solo aseguramos que no falle al llamar métodos básicos
    svc.info('info msg')
    svc.debug('debug msg')
    svc.warning('warn msg')
    svc.error('error msg')
    assert True
