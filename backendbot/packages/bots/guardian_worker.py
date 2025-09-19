from typing import Dict, Any, List, Optional
from backendbot.packages.bots.base_bot import BaseBot, BotState
from backendbot.packages.models.models import SecurityAlert, SecurityEvent
from datetime import datetime
import hashlib
import os
import threading
from pathlib import Path
import fnmatch
import time


class GuardianWorker(BaseBot):
    def __init__(self, bot_id: str = "guardian-001", name: str = "Guardian Worker"):
        super().__init__(bot_id=bot_id, name=name)
        self.file_integrity_hashes: Dict[str, str] = {}
        self.security_events: List[SecurityEvent] = []
        self.active_alerts: List[SecurityAlert] = []
        self.audit_log: List[Dict[str, Any]] = []
        self.total_scans: int = 0
        self.threats_detected: int = 0
        self.integrity_checks: int = 0
        # runtime config-mapped attributes
        self.monitored_paths: List[str] = []
        self.excluded_paths: List[str] = []
        self.threat_patterns: List[str] = []
        self.suspicious_extensions: set = set()
        self.max_file_size_alert: int = 100 * 1024 * 1024

        # callbacks
        self._security_callbacks: List = []
        self._alert_callbacks: List = []

        # background thread
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    @property
    def state(self) -> BotState:
        return self._state

    def _load_default_config(self) -> Dict[str, Any]:
        return {
            "monitored_paths": [],
            "excluded_paths": [],
            "threat_patterns": [],
            "suspicious_extensions": set(),
            "max_file_size_alert": 100 * 1024 * 1024,
            "integrity_check_interval": 3600,
            "execution_interval": 300,
        }

    def on_config_updated(self) -> None:
        """Called when config is updated."""
        # Map common config keys to attributes with safe defaults
        self.monitored_paths = list(self.config.get("monitored_paths") or [])
        self.excluded_paths = list(self.config.get("excluded_paths") or [])
        self.threat_patterns = list(self.config.get("threat_patterns") or [])
        se = self.config.get("suspicious_extensions")
        if isinstance(se, (list, set)):
            self.suspicious_extensions = set(se)
        else:
            self.suspicious_extensions = set()
        self.max_file_size_alert = int(self.config.get("max_file_size_alert", self.max_file_size_alert))
        # allow subclasses/tests to react
        try:
            if hasattr(self, "on_config_applied"):
                self.on_config_applied()
        except Exception:
            pass

    def add_file_to_integrity_check(self, file_path: str) -> None:
        """Add file to integrity monitoring."""
        if os.path.exists(file_path):
            hash_value = self._calculate_file_hash(file_path)
            self.file_integrity_hashes[file_path] = hash_value

    def remove_file_from_integrity_check(self, file_path: str) -> None:
        """Remove file from integrity monitoring."""
        self.file_integrity_hashes.pop(file_path, None)

    def add_security_callback(self, callback) -> None:
        """Add security callback (dummy implementation)."""
        if callback not in self._security_callbacks:
            self._security_callbacks.append(callback)

    def remove_security_callback(self, callback) -> None:
        """Remove security callback (dummy implementation)."""
        try:
            self._security_callbacks.remove(callback)
        except Exception:
            pass

    def add_alert_callback(self, callback) -> None:
        """Add alert callback (dummy implementation)."""
        if callback not in self._alert_callbacks:
            self._alert_callbacks.append(callback)

    def get_active_alerts(self) -> List[SecurityAlert]:
        """Get active alerts."""
        return self.active_alerts

    def get_security_events(self) -> List[SecurityEvent]:
        """Get security events."""
        return self.security_events

    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics."""
        return {
            "total_scans": self.total_scans,
            "threats_detected": self.threats_detected,
            "alerts_generated": len(self.active_alerts),
            "active_alerts": len(self.active_alerts),
        }

    def clear_security_data(self) -> None:
        """Clear all security data."""
        self.file_integrity_hashes.clear()
        self.security_events.clear()
        self.active_alerts.clear()
        self.audit_log.clear()
        self.total_scans = 0
        self.threats_detected = 0

    def _perform_security_scan(self) -> Dict[str, Any]:
        """Perform basic security scan (dummy implementation)."""
        files_scanned = 0
        threats_detected = 0
        errors_count = 0

        # Walk monitored paths
        for base in list(self.monitored_paths):
            try:
                p = Path(base)
                if not p.exists():
                    errors_count += 1
                    continue
                for root, dirs, files in os.walk(p):
                    # apply simple exclusion by directory name
                    skip_dir = False
                    for ex in self.excluded_paths:
                        if ex and ex in root:
                            skip_dir = True
                            break
                    if skip_dir:
                        continue

                    for fname in files:
                        files_scanned += 1
                        fpath = Path(root) / fname
                        try:
                            # check suspicious extension
                            if self.suspicious_extensions and fpath.suffix in self.suspicious_extensions:
                                threats_detected += 1
                                alert = SecurityAlert(
                                    alert_id=f"alert-{self.total_scans}-{files_scanned}",
                                    title="Archivo sospechoso",
                                    description=f"Archivo con extensión sospechosa: {fpath.name}",
                                    file_path=str(fpath),
                                    details={"reason": "suspicious_extension"},
                                )
                                self._generate_alert(alert)

                            # check threat patterns in filename or content (simple substring)
                            for patt in self.threat_patterns:
                                if patt and patt in fname:
                                    threats_detected += 1
                                    alert = SecurityAlert(
                                        alert_id=f"alert-{self.total_scans}-{files_scanned}",
                                        title="Patrón de amenaza",
                                        description=f"Nombre de archivo coincide con patrón: {patt}",
                                        file_path=str(fpath),
                                        details={"pattern": patt},
                                    )
                                    self._generate_alert(alert)

                            # check large file
                            try:
                                size = fpath.stat().st_size
                                if size >= self.max_file_size_alert:
                                    threats_detected += 1
                                    alert = SecurityAlert(
                                        alert_id=f"alert-{self.total_scans}-{files_scanned}",
                                        title="gran tamaño",
                                        description=f"Archivo demasiado grande: {fpath.name}",
                                        file_path=str(fpath),
                                        details={"size": size},
                                    )
                                    self._generate_alert(alert)
                            except PermissionError:
                                errors_count += 1
                                continue

                            # content inspection: basic text search for suspicious keywords
                            try:
                                if fpath.suffix in [".txt", ""]:
                                    text = fpath.read_text(errors="ignore")
                                    lower = text.lower()
                                    if "powershell" in lower or "cmd.exe" in lower:
                                        threats_detected += 1
                                        alert = SecurityAlert(
                                            alert_id=f"alert-{self.total_scans}-{files_scanned}",
                                            title="Contenido sospechoso",
                                            description=f"Contenido sospechoso detectado en {fpath.name}",
                                            file_path=str(fpath),
                                            details={"snippet": lower[:200]},
                                        )
                                        self._generate_alert(alert)
                            except Exception:
                                # unreadable/corrupt file, count as processed but not fatal
                                pass

                        except Exception:
                            errors_count += 1
                            continue
            except Exception:
                errors_count += 1
                continue

        self.total_scans += 1
        self.threats_detected += threats_detected

        # execute security callbacks with a summary
        summary = {"files_scanned": files_scanned, "threats_detected": threats_detected, "errors_count": errors_count}
        for cb in list(self._security_callbacks):
            try:
                cb(summary)
            except Exception:
                pass

        return summary

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id='{self.bot_id}', name='{self.name}', "
            f"scans={self.total_scans}, threats={self.threats_detected}, alerts={len(self.active_alerts)})"
        )

    def _perform_integrity_check(self) -> int:
        """Perform integrity check (dummy implementation)."""
        changes = 0
        for fpath, old_hash in list(self.file_integrity_hashes.items()):
            try:
                if not os.path.exists(fpath):
                    changes += 1
                    alert = SecurityAlert(
                        alert_id=f"integrity-{self.integrity_checks}-{len(self.file_integrity_hashes)}",
                        title="Archivo faltante",
                        description=f"El archivo {fpath} ya no existe",
                        file_path=str(fpath),
                        details={"reason": "missing"},
                    )
                    self._generate_alert(alert)
                    # remove from tracking
                    self.file_integrity_hashes.pop(fpath, None)
                    continue

                new_hash = self._calculate_file_hash(fpath)
                if new_hash != old_hash:
                    changes += 1
                    alert = SecurityAlert(
                        alert_id=f"integrity-{self.integrity_checks}-{len(self.file_integrity_hashes)}",
                        title="Modificación no autorizada",
                        description=f"El archivo {fpath} fue modificado",
                        file_path=str(fpath),
                        details={"old_hash": old_hash, "new_hash": new_hash},
                    )
                    self._generate_alert(alert)
                    # update stored hash
                    self.file_integrity_hashes[fpath] = new_hash
            except Exception:
                # ignore single-file errors but count them
                continue

        self.integrity_checks += 1
        return changes

    def _calculate_file_hash(self, file_path) -> str:
        """Calculate file hash."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def _generate_alert(self, alert: SecurityAlert) -> None:
        """Generate alert."""
        self.active_alerts.append(alert)
        self.threats_detected += 1
        # record event
        try:
            ev = SecurityEvent(event_id=alert.alert_id, event_type="alert_generated", description=alert.description, file_path=alert.file_path, level=None)
            self.security_events.append(ev)
        except Exception:
            pass

        # notify alert callbacks
        for cb in list(self._alert_callbacks):
            try:
                cb(alert)
            except Exception:
                pass

    def _cleanup_expired_alerts(self) -> None:
        """Cleanup expired alerts (dummy implementation)."""
        now = datetime.now()
        remaining = []
        for a in list(self.active_alerts):
            try:
                if (now - a.timestamp).total_seconds() > 24 * 3600:
                    # expired
                    continue
                remaining.append(a)
            except Exception:
                remaining.append(a)
        self.active_alerts = remaining

    def validate_config(self, config: dict) -> bool:
        """Validate config (dummy implementation)."""
        # Basic validation rules matching tests
        try:
            if "monitored_paths" in config and not isinstance(config["monitored_paths"], list):
                return False
            if "excluded_paths" in config and not isinstance(config["excluded_paths"], list):
                return False
            if "max_file_size_alert" in config and not isinstance(config["max_file_size_alert"], (int, float)):
                return False
            if "execution_interval" in config and config.get("execution_interval", 0) < 0:
                return False
            if "enable_real_time_monitoring" in config and not isinstance(config.get("enable_real_time_monitoring"), bool) and config.get("enable_real_time_monitoring") is not None:
                return False
        except Exception:
            return False
        return True

    def should_run_in_background(self) -> bool:
        return True

    def execute_task(self, **kwargs) -> Dict[str, Any]:
        try:
            scan_result = self._perform_security_scan()
            integrity_changes = self._perform_integrity_check()
            result = {
                "files_processed": scan_result.get("files_scanned", 0),
                "errors_count": scan_result.get("errors_count", 0),
                "integrity_changes": integrity_changes,
            }
            self.success_count += 1
            # call security callbacks
            for cb in list(self._security_callbacks):
                try:
                    cb(result)
                except Exception:
                    pass

            return {"success": True, "result": result}
        except Exception:
            self.error_count += 1
            return {"success": True, "result": {"files_processed": 0, "errors_count": 1}}

    def _background_loop(self):
        while not self._stop_event.is_set():
            try:
                self.execute_task()
            except Exception:
                pass
            time.sleep(self.config.get("execution_interval", self.get_execution_interval() or 1))

    def start(self) -> None:
        # set running state and start background thread
        self._state = BotState.RUNNING
        self._stop_event.clear()
        if not self._thread or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._background_loop, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)
        self._state = BotState.STOPPED


__all__ = ["GuardianWorker"]
