"""backendbot.core.config_manager
================================

Utilities for loading/saving application settings from/to the database.

The DatabaseConfigManager is intentionally forgiving: on missing tables or
transient DB errors it logs a warning and leaves the in-memory Pydantic
`Settings` object untouched (so the application can continue using defaults).

This module provides a thin, test-friendly shim used by the orchestrator and
by tests that expect DB-backed settings.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from .config import Settings
from .database.manager import get_db
from .database.models import Setting
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)


class DatabaseConfigManager:
    """Load and persist application settings using the DB as a secondary store.

    Design goals:
    - Non-fatal: if DB isn't available or table is missing, fall back to defaults.
    - Safe parsing: tolerate malformed JSON in DB and log the offending key.
    - Test-friendly: avoid side effects that require a real DB during unit tests.
    """

    def __init__(self, settings: Settings, auto_load: bool = True) -> None:
        self.settings = settings
        if auto_load:
            self.load_from_db()

    def load_from_db(self) -> None:
        """Load available settings from DB and apply them to the Pydantic object.

        The DB is considered a secondary source; only top-level keys are applied
        in this implementation. A production implementation should validate and
        map values carefully (nested updates, type coercion, secrets handling).
        """
        try:
            with get_db() as db:
                db_settings = db.query(Setting).all()
        except OperationalError:
            logger.warning("Database unavailable or 'settings' table missing; using defaults")
            return
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Unexpected error reading settings from DB: %s", exc)
            return

        for s in db_settings:
            try:
                parsed = json.loads(s.value)
            except Exception:
                logger.warning("Malformed JSON for setting '%s' - skipping", s.key)
                continue

            # Only set attributes that already exist on settings
            if hasattr(self.settings, s.key):
                try:
                    setattr(self.settings, s.key, parsed)
                except Exception:
                    logger.warning("Failed to set settings.%s - skipping", s.key)

    def save_to_db(self) -> None:
        """Persist the current settings to the DB.

        This method writes each top-level key as a JSON string. It is intentionally
        simple; callers that need transactional guarantees should wrap calls
        accordingly.
        """
        try:
            with get_db() as db:
                settings_dict = self.settings.dict()
                for key, value in settings_dict.items():
                    raw = json.dumps(value)
                    db_setting = db.query(Setting).filter_by(key=key).first()
                    if db_setting:
                        db_setting.value = raw
                    else:
                        db.add(Setting(key=key, value=raw))
                db.commit()
        except OperationalError:
            logger.warning("Cannot persist settings to DB: database unavailable")
        except Exception:
            logger.exception("Unexpected error while saving settings to DB")

    def get_settings(self) -> Settings:
        """Return the in-memory Settings object."""
        return self.settings

    def get_all_config(self) -> dict:
        """Return the settings as a plain dictionary."""
        return self.settings.dict()

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value supporting dot notation.

        Example: `get('app.name', 'BackendBot')`
        """
        if not key:
            return default

        keys = key.split(".")
        value: Any = self.settings.dict()
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

