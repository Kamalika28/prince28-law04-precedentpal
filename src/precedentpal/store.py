"""In-memory read-only store loaded from the configured JSON file."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class RecordStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.records: list[dict[str, Any]] = []
        self.loaded = False

    def load(self) -> bool:
        """Load a JSON array; return False instead of crashing on missing/bad data."""
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(payload, list) or not all(isinstance(row, dict) for row in payload):
                raise ValueError("records file must contain a JSON array of objects")
            self.records = payload
            self.loaded = True
            logger.info("records loaded", extra={"records": len(self.records)})
            return True
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            self.records = []
            self.loaded = False
            logger.error("could not load records: %s", exc)
            return False

    def list(self, query: str | None = None) -> list[dict[str, Any]]:
        if not query:
            return list(self.records)
        needle = query.casefold()
        return [
            record
            for record in self.records
            if needle in " ".join(str(value) for value in record.values()).casefold()
        ]

    def get(self, record_id: str) -> dict[str, Any] | None:
        return next((row for row in self.records if str(row.get("id")) == record_id), None)
