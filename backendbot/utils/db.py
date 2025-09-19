"""Wrapper de persistencia compatible con importaciones del proyecto.

Exporta `db_manager`, `config_manager`, `migration_manager` e `init_database`.
"""

from .database_manager import (config_manager, db_manager, init_database,
                               migration_manager)

__all__ = ["db_manager", "config_manager", "migration_manager", "init_database"]
# Este módulo está deshabilitado. No se utiliza base de datos externa en BackendBot.
