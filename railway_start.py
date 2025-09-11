#!/usr/bin/env python3
import os
import sys
import uvicorn
from pathlib import Path

# Add src to path for Railway
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from backendbot.main import app
    print("✅ BackendBot app loaded successfully")
except ImportError as e:
    print(f"❌ Error importing app: {e}")
    sys.exit(1)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")

    print(f"🚀 Starting BackendBot on {host}:{port}")

    uvicorn.run(
        "backendbot.main:app",
        host=host,
        port=port,
        reload=False,
        workers=1,
        loop="uvloop",
        http="httptools",
        log_level="info"
    )