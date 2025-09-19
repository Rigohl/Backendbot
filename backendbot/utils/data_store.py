import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(".backendbot_data")

DEFAULT_FILES: dict[str, Any] = {
    "usage_patterns.json": {},
    "user_preferences.json": {},
    "performance_metrics.json": {},
    "scheduled_tasks.json": [],
    "file_index.json": {},
}


def ensure_data_dir():
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def _file_path(name: str) -> Path:
    ensure_data_dir()
    return DATA_DIR / name


def read_json(name: str):
    p = _file_path(name)
    if not p.exists():
        # create with default
        default = DEFAULT_FILES.get(name, {})
        try:
            p.write_text(json.dumps(default, indent=2), encoding="utf-8")
        except Exception:
            pass
        return default
    try:
        text = p.read_text(encoding="utf-8")
        if not text.strip():
            return DEFAULT_FILES.get(name, {})
        return json.loads(text)
    except Exception:
        # Corrupted file: try to backup and recreate default
        try:
            backup = p.with_suffix(".bak")
            p.replace(backup)
        except Exception:
            pass
        return DEFAULT_FILES.get(name, {})


def write_json(name: str, data):
    p = _file_path(name)
    try:
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception:
        return False


def initialize_defaults():
    ensure_data_dir()
    for name, default in DEFAULT_FILES.items():
        p = _file_path(name)
        if not p.exists() or not p.read_text(encoding="utf-8").strip():
            try:
                p.write_text(
                    json.dumps(default, indent=2, ensure_ascii=False), encoding="utf-8"
                )
            except Exception:
                pass
