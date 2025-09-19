"""
Bots package for BackendBot
"""

from .manager import BotManager
from .monitor import MonitorBot
from .organizer import OrganizerBot
from .indexer import IndexerBot
from .guardian import GuardianBot
from .auditor_files import AuditorFilesBot
from .auditor_programs import AuditorProgramsBot

__all__ = [
    'BotManager',
    'MonitorBot',
    'OrganizerBot',
    'IndexerBot',
    'GuardianBot',
    'AuditorFilesBot',
    'AuditorProgramsBot'
]