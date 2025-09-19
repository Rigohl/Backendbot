"""
Utilities to load environment variables and .env files tolerantly.

Used by entrypoints to avoid crashes when `.env` files contain invalid
encoding or unexpected lines.
"""
import logging
import os
from pathlib import Path

logger = logging.getLogger("backendbot.env_loader")


def load_env(env_path: str | None = None) -> None:
    """Load environment variables from a .env file if present.

    This function is intentionally tolerant: it will try to read the
    file as UTF-8 and then as Latin-1 if UTF-8 fails, ignoring parse
    errors and logging warnings rather than raising.
    """
    if env_path is None:
        env_path = os.environ.get("DOTENV_FILE", ".env")

    p = Path(env_path)
    if not p.exists():
        return

    text = None
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        try:
            text = p.read_text(encoding="latin-1")
            logger.warning("Loaded .env using latin-1 fallback: %s", p)
        except Exception:
            logger.exception("Failed to read .env file: %s", p)
            return

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            logger.debug("Skipping invalid .env line: %s", line)
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val
