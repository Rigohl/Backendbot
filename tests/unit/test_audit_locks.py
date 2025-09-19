import os
import threading
import time
from pathlib import Path

from backendbot.core.audit import record_audit, AUDIT_DIR
from backendbot.core.locks import with_lock


def test_record_audit_writes_file(tmp_path):
    # override audit dir for test
    audit_dir = tmp_path / "audit"
    os.environ["BACKENDBOT_AUDIT_DIR"] = str(audit_dir)
    # monkeypatch module constant
    from importlib import reload

    import backendbot.core.audit as audit_mod

    audit_mod.AUDIT_DIR = audit_dir

    ev = record_audit({"actor": "test", "action": "run"})
    files = list(audit_dir.glob("*.jsonl"))
    assert len(files) == 1
    content = files[0].read_text(encoding="utf-8").strip()
    assert "event_id" in content
    assert "actor" in content


def test_with_lock_blocks(tmp_path):
    lock_file = tmp_path / "my.lock"
    results = []

    def worker(id_):
        with with_lock(lock_file, timeout=5):
            results.append(f"start-{id_}")
            time.sleep(0.1)
            results.append(f"end-{id_}")

    t1 = threading.Thread(target=worker, args=(1,))
    t2 = threading.Thread(target=worker, args=(2,))
    t1.start()
    time.sleep(0.02)
    t2.start()
    t1.join()
    t2.join()

    # Ensure that lock serialized the critical sections
    assert results[0].startswith("start-1")
    assert results[1].startswith("end-1")
    assert results[2].startswith("start-2")
    assert results[3].startswith("end-2")
