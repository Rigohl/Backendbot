import time # Added import
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import OptimizationEvent, ProcessHistory, WatchdogDecision


class HistoryRepository:
    """Repository layer for historical data.
    Encapsulates database operations related to process history,
    optimization events, and watchdog decisions.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_process_history(
        self, limit: int, offset: int
    ) -> List[Dict[str, Any]]:
        """Fetches historical process data."""
        result = await self.session.execute(
            select(ProcessHistory)
            .order_by(ProcessHistory.timestamp.desc())
            .offset(offset)
            .limit(limit)
        )
        return [row.to_dict() for row in result.scalars().all()]

    async def get_optimization_history(
        self, limit: int, offset: int
    ) -> List[Dict[str, Any]]:
        """Fetches historical optimization event data."""
        result = await self.session.execute(
            select(OptimizationEvent)
            .order_by(OptimizationEvent.timestamp.desc())
            .offset(offset)
            .limit(limit)
        )
        return [row.to_dict() for row in result.scalars().all()]

    async def get_decision_history(
        self, limit: int, offset: int
    ) -> List[Dict[str, Any]]:
        """Fetches historical watchdog decision data."""
        result = await self.session.execute(
            select(WatchdogDecision)
            .order_by(WatchdogDecision.timestamp.desc())
            .offset(offset)
            .limit(limit)
        )
        return [row.to_dict() for row in result.scalars().all()]

    async def store_process_data(self, pid: int, name: str, ram_mb: float, cpu_percent: float) -> None:
        """Stores process data in the database."""
        new_entry = ProcessHistory(
            timestamp=time.time(),
            pid=pid,
            name=name,
            ram_mb=ram_mb,
            cpu_percent=cpu_percent,
        )
        self.session.add(new_entry)
        await self.session.commit()

    async def store_optimization_event(self, freed_ram_mb: float) -> None:
        """Stores optimization event in the database."""
        new_entry = OptimizationEvent(
            timestamp=time.time(),
            freed_ram_mb=freed_ram_mb
        )
        self.session.add(new_entry)
        await self.session.commit()

    async def store_watchdog_decision(
        self, program_name: str, action: str, cpu_usage: float | None = None, ram_usage: float | None = None
    ) -> None:
        """Stores watchdog decision in the database."""
        new_entry = WatchdogDecision(
            timestamp=time.time(),
            program_name=program_name,
            action=action,
            cpu_usage=cpu_usage,
            ram_usage=ram_usage,
        )
        self.session.add(new_entry)
        await self.session.commit()

