"""MemoryItem — 长期记忆数据模型 + SQLite 持久化存储。"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


# Python 3.10 兼容：StrEnum 是 3.11+ 才有的
class _StrEnum(str, Enum):
    def __str__(self) -> str:
        return str(self.value)


# Python 3.10 兼容：datetime.UTC 是 3.11+ 才有的
_UTC = timezone.utc


class MemoryTier(_StrEnum):
    """记忆分层：工作记忆 / 短期 / 长期。"""

    WORKING = "working"
    SHORT = "short"
    LONG = "long"


class MemoryItem(BaseModel):
    """一条长期记忆。"""

    id: str = Field(default_factory=lambda: f"mem_{uuid4().hex[:12]}")
    content: str
    tier: MemoryTier = MemoryTier.LONG
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    source: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(_UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(_UTC))
    ttl_seconds: int | None = None

    def is_expired(self) -> bool:
        """Check whether this item has passed its TTL."""
        if self.ttl_seconds is None:
            return False
        expiry = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.now(_UTC) > expiry


# ═══════════════════════════════════════════════════════════
# SQLite 持久化存储
# ═══════════════════════════════════════════════════════════


class PersistentMemoryStore:
    """SQLite-backed long-term memory store."""

    def __init__(self, db_path: str | Path = "data/memory.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
        return self._conn

    def _init_db(self) -> None:
        conn = self._connect()
        conn.execute(
            "CREATE TABLE IF NOT EXISTS memories ("
            "id TEXT PRIMARY KEY, "
            "content TEXT NOT NULL, "
            "tier TEXT NOT NULL DEFAULT 'long', "
            "importance REAL DEFAULT 0.5, "
            "source TEXT, "
            "tags TEXT DEFAULT '[]', "
            "metadata TEXT DEFAULT '{}', "
            "created_at TEXT NOT NULL, "
            "updated_at TEXT NOT NULL, "
            "ttl_seconds INTEGER)"
        )
        conn.commit()

    def save(self, item: MemoryItem) -> None:
        conn = self._connect()
        conn.execute(
            "INSERT OR REPLACE INTO memories "
            "(id, content, tier, importance, source, tags, metadata, created_at, updated_at, ttl_seconds)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                item.id,
                item.content,
                item.tier.value,
                item.importance,
                item.source,
                str(item.tags),
                str(item.metadata),
                item.created_at.isoformat(),
                item.updated_at.isoformat(),
                item.ttl_seconds,
            ),
        )
        conn.commit()

    def save_batch(self, items: list[MemoryItem]) -> None:
        for item in items:
            self.save(item)

    def retrieve(
        self,
        query: str = "",
        tier: MemoryTier | None = None,
        tags: list[str] | None = None,
        limit: int = 10,
    ) -> list[MemoryItem]:
        conn = self._connect()
        sql = "SELECT * FROM memories WHERE 1=1"
        params: list[Any] = []

        if query:
            sql += " AND content LIKE ?"
            params.append(f"%{query}%")
        if tier:
            sql += " AND tier = ?"
            params.append(tier.value)
        if tags:
            for tag in tags:
                sql += " AND tags LIKE ?"
                params.append(f"%{tag}%")

        sql += " ORDER BY importance DESC, created_at DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(sql, params).fetchall()
        return [self._row_to_item(r) for r in rows]

    def delete(self, item_id: str) -> None:
        conn = self._connect()
        conn.execute("DELETE FROM memories WHERE id = ?", (item_id,))
        conn.commit()

    def cleanup_expired(self) -> int:
        """Remove expired items. Returns count deleted."""
        conn = self._connect()
        now = datetime.now(_UTC).isoformat()
        result = conn.execute(
            "DELETE FROM memories WHERE ttl_seconds IS NOT NULL "
            "AND datetime(created_at, '+' || ttl_seconds || ' seconds') < ?",
            (now,),
        )
        conn.commit()
        return result.rowcount

    def count(self) -> int:
        conn = self._connect()
        row = conn.execute("SELECT COUNT(*) FROM memories").fetchone()
        return int(row[0]) if row else 0

    @staticmethod
    def _row_to_item(row: sqlite3.Row) -> MemoryItem:
        import ast

        return MemoryItem(
            id=row["id"],
            content=row["content"],
            tier=MemoryTier(row["tier"]),
            importance=row["importance"],
            source=row["source"],
            tags=ast.literal_eval(row["tags"]) if row["tags"] else [],
            metadata=ast.literal_eval(row["metadata"]) if row["metadata"] else {},
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            ttl_seconds=row["ttl_seconds"],
        )

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
