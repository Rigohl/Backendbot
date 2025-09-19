"""
Small integration for environment loading used by entrypoints and services.

This module delegates to `tools.env_loader.load_env()` and provides a
convenience `ensure_loaded()` function that callers can import and call
at process start.
"""
from __future__ import annotations

import logging
from typing import Optional

from tools.env_loader import load_env

logger = logging.getLogger("backendbot.core.env")


def ensure_loaded(env_path: Optional[str] = None) -> None:
    """Ensure environment variables from `.env` are loaded without raising.

    Call this early in process startup (entrypoint) to prefer OS env vars
    while filling missing variables from a `.env` file.
    """
    try:
        load_env(env_path)
    except Exception:
        logger.exception("Unexpected error while loading .env (ignored)")
