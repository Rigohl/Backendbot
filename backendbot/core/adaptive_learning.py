"""Minimal adaptive learning compatibility shim.

Provides an `adaptive_learning` object with the small API surface required
by UI components and tests: record_user_action, record_performance_metric,
get_recommendations, get_learning_stats.
"""

from typing import Any, Dict, List


class _AdaptiveLearning:
    def __init__(self) -> None:
        self._actions = []
        self._metrics = []

    def record_user_action(
        self, user_id: str, action: str, metadata: Dict[str, Any] | None = None
    ) -> None:
        self._actions.append(
            {"user_id": user_id, "action": action, "metadata": metadata}
        )

    def record_performance_metric(self, name: str, value: Any) -> None:
        self._metrics.append({"name": name, "value": value})

    def get_recommendations(self) -> List[Dict[str, Any]]:
        # Return simple mocked recommendations
        return [{"score": 0.5, "suggestion": "Try cleaning cache"}]

    def get_learning_stats(self) -> Dict[str, int]:
        return {"actions": len(self._actions), "metrics": len(self._metrics)}


adaptive_learning = _AdaptiveLearning()

__all__ = ["adaptive_learning"]
