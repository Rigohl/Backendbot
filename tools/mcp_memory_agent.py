"""Lightweight MCP Memory agent (background process).

Usage: run in background; write JSON lines to infra/memory_log.jsonl via the `record_note` function or CLI.
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime


STORAGE = Path(__file__).resolve().parents[1] / 'infra' / 'memory_log.jsonl'
STORAGE.parent.mkdir(parents=True, exist_ok=True)


def record_note(kind: str, message: str, metadata: dict | None = None) -> None:
    entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'kind': kind,
        'message': message,
        'metadata': metadata or {}
    }
    with open(STORAGE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def run_loop(poll_interval: float = 1.0):
    # Simple loop that writes a heartbeat so the file shows agent is alive
    try:
        while True:
            record_note('heartbeat', 'mcp_memory_agent alive')
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        record_note('shutdown', 'mcp_memory_agent stopped by user')


def main(argv):
    if len(argv) >= 2 and argv[1] == 'record':
        # CLI: tools/mcp_memory_agent.py record "message"
        msg = argv[2] if len(argv) > 2 else ''
        record_note('manual', msg)
        print('ok')
        return 0

    run_loop()


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
