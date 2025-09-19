from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .locks import with_lock


AUDIT_DIR = Path("data/audit")


def _ensure_audit_dir() -> None:
    if not AUDIT_DIR.exists():
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def record_audit(event: Dict[str, Any]) -> Dict[str, Any]:
    """Record a single audit event as JSONL into data/audit/YYYY-MM-DD.jsonl.

    The function returns the event augmented with `event_id` and `timestamp`.
    """
    _ensure_audit_dir()
    date = datetime.utcnow().date().isoformat()
    file_path = AUDIT_DIR / f"{date}.jsonl"

    # Normalize event and add metadata
    ev = dict(event)
    ev.setdefault("event_id", str(uuid.uuid4()))
    ev.setdefault("timestamp", datetime.utcnow().isoformat() + "Z")

    lock_path = AUDIT_DIR / f"{date}.lock"
    with with_lock(lock_path, timeout=2.0):
        with open(file_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

    return ev
