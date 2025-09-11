from typing import List, Dict, Any

from ..repositories.history_repository import HistoryRepository

class HistoryService:
    """
    Service layer for historical data.
    Provides business logic for retrieving historical data,
    depending on HistoryRepository for data access.
    """
    def __init__(self, repository: HistoryRepository):
        self.repository = repository

    async def get_process_history(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Retrieves historical process data from the repository."""
        return await self.repository.get_process_history(limit, offset)

    async def get_optimization_history(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Retrieves historical optimization event data from the repository."""
        return await self.repository.get_optimization_history(limit, offset)

    async def get_decision_history(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Retrieves historical watchdog decision data from the repository."""
        return await self.repository.get_decision_history(limit, offset)