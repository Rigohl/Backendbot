"""
Canonical entrypoint to run API + executor/orchestrator

Usage:
    python run_backendbot.py         # runs both API and executor

This script starts Uvicorn for the FastAPI app (if available) and
starts a background executor process (if a `start_executor` callable
is available in `backendbot.executor` or `backendbot.core.executor`).
It performs safe imports and handles graceful shutdown on SIGINT/SIGTERM.
"""
import asyncio
import importlib
import logging
import signal
import sys
from typing import Optional

from tools.env_loader import load_env

logger = logging.getLogger("backendbot.entrypoint")


async def _run_uvicorn(app_module: str, host: str = "127.0.0.1", port: int = 8000):
    try:
        import uvicorn
    except Exception:
        logger.warning("uvicorn is not installed; skipping API server start")
        return None

    # uvicorn.run blocks; use Config + Server to run inside asyncio
    try:
        mod = importlib.import_module(app_module)
        app = getattr(mod, "app", None)
        if app is None:
            logger.warning("module %s has no attribute 'app' — skipping API start", app_module)
            return None

        config = uvicorn.Config(app=app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    except Exception:
        logger.exception("Failed to start API server (%s)", app_module)


async def _maybe_start_executor() -> Optional[asyncio.Task]:
    # Look for a start function in common locations
    candidates = [
        "backendbot.executor",
        "backendbot.core.executor",
        "executor",
    ]
    for modname in candidates:
        try:
            mod = importlib.import_module(modname)
            starter = getattr(mod, "start_executor", None) or getattr(mod, "start", None)
            if callable(starter):
                logger.info("Starting executor from %s", modname)
                # If it's a coroutine function, schedule it
                if asyncio.iscoroutinefunction(starter):
                    return asyncio.create_task(starter())
                else:
                    loop = asyncio.get_event_loop()
                    return loop.run_in_executor(None, starter)
        except Exception:
            logger.debug("executor module %s not available or failed to import", modname)
    logger.info("No executor starter found; skipping executor")
    return None


def _setup_signal_handlers(loop: asyncio.AbstractEventLoop, tasks):
    def _stop():
        logger.info("Shutdown requested — cancelling tasks")
        for t in tasks:
            try:
                t.cancel()
            except Exception:
                pass

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _stop)
        except NotImplementedError:
            # Windows: add_signal_handler may not be available in some event loops
            signal.signal(sig, lambda *_: _stop())


async def main():
    load_env()  # load .env if present (tolerant)

    loop = asyncio.get_event_loop()
    tasks = []

    # Start executor (non-blocking)
    executor_task = await _maybe_start_executor()
    if executor_task is not None:
        if isinstance(executor_task, asyncio.Task):
            tasks.append(executor_task)

    # Start API server if backend app exists
    # Common FastAPI app locations
    api_candidates = [
        "api_server",  # root api_server.py
        "apps.api.app",  # apps/api/app.py
        "backendbot.api.app",
        "backendbot.apps.api.app",
    ]
    api_started = False
    for candidate in api_candidates:
        try:
            # try to import module; if exists, run uvicorn
            importlib.import_module(candidate)
            api_started = True
            await _run_uvicorn(candidate)
            break
        except Exception:
            continue

    if not api_started:
        logger.info("No API candidate found to start")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted")
    except Exception:
        logger.exception("Entrypoint failed")
        sys.exit(1)
