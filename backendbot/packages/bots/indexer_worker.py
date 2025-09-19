from typing import Dict, Any
from backendbot.packages.bots.base_bot import BaseBot
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class FileIndex:
    path: str
    name: str
    extension: str
    size: int
    modified_time: datetime
    created_time: datetime
    content_hash: str
    mime_type: str
    line_count: int = 0
    word_count: int = 0
    is_binary: bool = False
    tags: list = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileIndex":
        data = dict(data)
        # Ensure tags default
        if "tags" not in data:
            data["tags"] = []
        return cls(**data)


@dataclass
class SearchResult:
    file_index: FileIndex
    relevance_score: float
    matched_terms: list
    context: str = ""


class IndexerWorker(BaseBot):
    def __init__(self, bot_id: str = "indexer-001", name: str = "Indexer Worker"):
        super().__init__(bot_id=bot_id, name=name)

    def should_run_in_background(self) -> bool:
        return True

    def execute_task(self, **kwargs) -> Dict[str, Any]:
        self.success_count += 1
        return {"success": True, "indexed": 0}


__all__ = ["IndexerWorker"]
