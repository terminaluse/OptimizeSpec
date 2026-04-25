from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SkillRegistryEntry:
    fingerprint: str
    logical_key: str
    skill_id: str
    version: str
    display_title: str | None = None


class LocalSkillRegistry:
    def __init__(self, path: Path) -> None:
        self.path = path

    def find_by_fingerprint(self, fingerprint: str) -> SkillRegistryEntry | None:
        for entry in reversed(self._load_entries()):
            if entry.fingerprint == fingerprint:
                return entry
        return None

    def find_latest_by_logical_key(self, logical_key: str) -> SkillRegistryEntry | None:
        for entry in reversed(self._load_entries()):
            if entry.logical_key == logical_key:
                return entry
        return None

    def record(
        self,
        *,
        fingerprint: str,
        logical_key: str,
        skill_id: str,
        version: str,
        display_title: str | None,
    ) -> SkillRegistryEntry:
        entries = self._load_raw()
        record = {
            "fingerprint": fingerprint,
            "logical_key": logical_key,
            "skill_id": skill_id,
            "version": version,
            "display_title": display_title,
        }
        for index, existing in enumerate(entries):
            if existing.get("fingerprint") == fingerprint:
                entries[index] = record
                break
        else:
            entries.append(record)
        self._save_raw(entries)
        return SkillRegistryEntry(**record)

    def _load_entries(self) -> list[SkillRegistryEntry]:
        return [SkillRegistryEntry(**entry) for entry in self._load_raw()]

    def _load_raw(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        if not isinstance(payload, list):
            return []
        return [entry for entry in payload if isinstance(entry, dict)]

    def _save_raw(self, entries: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(entries, indent=2, sort_keys=True), encoding="utf-8")
