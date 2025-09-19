from __future__ import annotations

import contextlib
import time
from pathlib import Path
from typing import Iterator

from filelock import Timeout, FileLock


def _ensure_parent(path: Path) -> None:
    parent = path.parent
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)


@contextlib.contextmanager
def with_lock(lock_path: str | Path, timeout: float = 5.0) -> Iterator[FileLock]:
    """Context manager that acquires a file lock for a path.

    Usage:
        with with_lock('data/audit/lockfile.lock'):
            # critical section

    Raises `filelock.Timeout` if the lock can't be acquired in time.
    """
    p = Path(lock_path)
    _ensure_parent(p)
    lock = FileLock(str(p))
    try:
        lock.acquire(timeout=timeout)
        yield lock
    finally:
        try:
            lock.release()
        except Exception:
            # Best-effort release
            pass
