"""Conftest para registrar fixtures compartidas desde tests.utils.test_utils"""

from tests.utils.test_utils import (
    TestConfig,
    create_mock_file,
    create_test_directory_structure,
    mock_system_info,
    mock_gpu_info,
    create_mock_database_data,
    MockDatabaseManager,
    TestDataFactory,
)

# Re-exportar fixtures definidos en test_utils (pytest los detectará aquí)
from tests.utils.test_utils import *  # noqa: F401,F403
