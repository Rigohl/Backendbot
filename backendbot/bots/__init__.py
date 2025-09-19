"""Bots package for BackendBot."""

from .auditor_files import AuditorFilesBot
from .auditor_programs import AuditorProgramsBot
from .guardian import GuardianBot
from .indexer import IndexerBot
from .manager import BotManager
from .monitor import MonitorBot
from .optimizer import OptimizerBot
from .organizer import OrganizerBot

__all__ = [
    "BotManager",
    "MonitorBot",
    "OrganizerBot",
    "IndexerBot",
    "GuardianBot",
    "AuditorFilesBot",
    "AuditorProgramsBot",
    "OptimizerBot",
]
