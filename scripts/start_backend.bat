@echo off
start "" python -m uvicorn src.backendbot.main:app --host 127.0.0.1 --port 8000 --log-level info
