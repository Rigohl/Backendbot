from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..utils import OptimizationEvent, ProcessHistory, WatchdogDecision


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
