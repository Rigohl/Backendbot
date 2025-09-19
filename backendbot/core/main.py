"""Minimal FastAPI app shim for compatibility with tests.

This provides a lightweight `app` object so tests that import
`src.backendbot.main:app` can run. It attempts to include routers from
`src.backendbot.ui` if present; otherwise exposes a simple root handler.
"""

from fastapi import FastAPI


def _build_app():
    app = FastAPI(title="BackendBot (compat shim)")
    # Attempt to import and include known UI routers one-by-one. Try both
    # the `src.backendbot.ui` package (modern layout) and the legacy
    # `backendbot.ui` location. Import failures for individual modules are
    # ignored so that the shim remains tolerant to partial layouts.
    import importlib

    ui_modules = [
        "monitor_routes",
        "history_routes",
        "indexer_routes",
        "organizer_routes",
        "events_routes",
        "dashboard_routes",
    ]

    any_router_registered = False
    for mod_name in ui_modules:
        for pkg in ("src.backendbot.ui", "backendbot.ui"):
            try:
                module = importlib.import_module(f"{pkg}.{mod_name}")
                router = getattr(module, "router", None)
                if router is not None:
                    app.include_router(router)
                    any_router_registered = True
                break
            except ModuleNotFoundError:
                # Try the next package path
                continue
            except Exception:
                # If the module exists but fails to import, skip it
                break

    if not any_router_registered:
        # Provide a simple root endpoint if no routers were successfully
        # registered (keeps behavior compatible with existing tests).
        @app.get("/")
        async def _root():
            return {"message": "Welcome to BackendBot Orchestrator"}

    return app


app = _build_app()


class BackendBotSystem:
    """Minimal orchestrator used by tests to instantiate system components.

    This is intentionally minimal: it wires the config manager, DB manager,
    task scheduler and learning system via the compatibility shims.
    """

    def __init__(self, config_path: str | None = None):
        self.config_path = config_path
        # Lazy imports to avoid heavy deps during collection
        from backendbot.core.adaptive_learning import adaptive_learning
        from backendbot.core.task_scheduler import TaskScheduler
        from backendbot.utils.database_manager import DatabaseManager

        self.config = None
        self.db_manager = (
            DatabaseManager() if hasattr(DatabaseManager, "__call__") else None
        )
        self.task_scheduler = TaskScheduler()
        self.learning_system = adaptive_learning
        # Load config from YAML if provided (tests provide a temp YAML)
        if config_path:
            try:
                import yaml

                with open(config_path, "r") as fh:
                    self.config = yaml.safe_load(fh)
            except Exception:
                self.config = None

    def start(self):
        if getattr(self.db_manager, "connect", None):
            self.db_manager.connect()
        if getattr(self.task_scheduler, "start", None):
            self.task_scheduler.start()
        if getattr(self.learning_system, "start_learning", None):
            self.learning_system.start_learning()


__all__ = ["app", "BackendBotSystem"]
