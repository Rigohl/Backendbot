from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator


class BotStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class BotInfo(BaseModel):
    id: str
    name: str
    status: BotStatus
    version: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationInfo(BaseModel):
    page: int = 1
    page_size: int = 10
    total_items: int = 25

    @property
    def computed_total_pages(self) -> int:
        if self.page_size <= 0:
            return 0
        return (self.total_items + self.page_size - 1) // self.page_size


class PaginatedResponse(BaseModel):
    success: bool
    message: str
    pagination: PaginationInfo = Field(default_factory=PaginationInfo)
    items: List[Any] = []


class SystemMetrics(BaseModel):
    cpu_usage: float = Field(ge=0.0, le=100.0)
    memory_usage: float = Field(ge=0.0, le=100.0)
    disk_usage: float = Field(ge=0.0, le=100.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SecurityAlert(BaseModel):
    alert_id: str
    title: str
    description: str
    file_path: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = Field(default_factory=dict)

    # Backwards-compatible aliases
    @property
    def id(self) -> str:  # pragma: no cover - thin alias
        return self.alert_id

    @property
    def level(self) -> str:  # pragma: no cover - thin alias
        return "n/a"

    @property
    def message(self) -> str:  # pragma: no cover - thin alias
        return self.description


class SecurityEvent(BaseModel):
    event_id: str
    event_type: str
    description: str
    file_path: Optional[str] = None
    level: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FileOrganizationResult(BaseModel):
    moved: int = 0
    errors: int = 0


class PowerInfo(BaseModel):
    percent: Optional[float] = None
    power_plugged: Optional[bool] = None
    secs_left: Optional[int] = None


class ThreatLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationInfo(BaseModel):
    id: str
    title: str
    message: str
    read: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class BackupType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class BackupInfo(BaseModel):
    id: str
    name: str
    type: BackupType
    source_paths: List[str]
    destination_path: str
    schedule: Optional[str] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: Optional[str] = "configured"
    enabled: bool = True



__all__ = [
    "BotStatus",
    "BotInfo",
    "APIResponse",
    "PaginationInfo",
    "PaginatedResponse",
    "SystemMetrics",
    "SecurityAlert",
    "SecurityEvent",
    "FileOrganizationResult",
    "PowerInfo",
    "ThreatLevel",
    "NotificationInfo",
]
