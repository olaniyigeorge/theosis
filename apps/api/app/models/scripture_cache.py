"""
Scripture text cache — Redis, not Postgres. This is deliberately outside
models/: it has no FK relationships, no review lifecycle, and per the PRD
should be fully disposable on a translation-license or provider swap without
touching the source-of-truth graph tables.

pip install redis pydantic
"""
from __future__ import annotations

import json
from datetime import timedelta

from pydantic import BaseModel, Field, field_validator
from redis.asyncio import Redis

# 30 days: long enough that steady-state traffic barely touches the Bible API,
# short enough that a translation swap self-heals within a month even if you
# forget to flush the namespace manually.
DEFAULT_TTL = timedelta(days=30)


class ScriptureCacheEntry(BaseModel):
    """
    Validated at the boundary where a Bible API response enters the system —
    this is the contract between "what the Bible API returned" and "what we
    trust enough to serve on read."
    """
    book: str
    chapter: int = Field(gt=0)
    verse: int = Field(gt=0)
    translation: str = Field(min_length=1, max_length=10)  # e.g. "ESV", "NIV"
    text: str = Field(min_length=1)
    fetched_at: str  # ISO 8601 — kept as str for trivial JSON round-trip

    @field_validator("translation")
    @classmethod
    def uppercase_translation(cls, v: str) -> str:
        return v.upper()

    def cache_key(self) -> str:
        return f"scripture:{self.book}:{self.chapter}:{self.verse}:{self.translation}"


class ScriptureCache:
    """Thin wrapper — nothing here should leak raw Redis calls into callers."""

    def __init__(self, redis: Redis, ttl: timedelta = DEFAULT_TTL) -> None:
        self._redis = redis
        self._ttl = ttl

    async def get(self, book: str, chapter: int, verse: int, translation: str) -> ScriptureCacheEntry | None:
        key = f"scripture:{book}:{chapter}:{verse}:{translation.upper()}"
        raw = await self._redis.get(key)
        if raw is None:
            return None
        return ScriptureCacheEntry.model_validate_json(raw)

    async def set(self, entry: ScriptureCacheEntry) -> None:
        await self._redis.set(entry.cache_key(), entry.model_dump_json(), ex=self._ttl)

    async def invalidate_translation(self, translation: str) -> int:
        """Call this on a translation-license swap — wipes only that translation's keys."""
        pattern = f"scripture:*:*:*:{translation.upper()}"
        keys = [k async for k in self._redis.scan_iter(match=pattern)]
        if keys:
            return await self._redis.delete(*keys)
        return 0