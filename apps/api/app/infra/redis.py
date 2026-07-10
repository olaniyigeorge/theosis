import json
import logging
import redis.asyncio as redis
from typing import Any, Optional

from config import settings

logger = logging.getLogger("app")


class RedisManager:
    """
    Single Redis client manager for the entire application.
    Initialized once at startup via lifespan, shared via app.state.redis.
    """

    def __init__(self) -> None:
        self.client: Optional[redis.Redis] = None

    async def initialize(
        self,
        url: str = settings.REDIS_URL,
        decode_responses: bool = True,
    ) -> redis.Redis:
        self.client = redis.from_url(url, decode_responses=decode_responses)
        await self.client.ping()
        logger.info("Redis connected (%s)", url)
        return self.client

    async def close(self) -> None:
        if self.client is None:
            return
        await self.client.aclose()
        self.client = None
        logger.info("Redis connection closed")

    def get(self) -> redis.Redis:
        if self.client is None:
            raise RuntimeError("RedisManager not initialized. Call initialize() first.")
        return self.client


redis_manager = RedisManager()


async def get_cache(key: str) -> Optional[Any]:
    try:
        client = redis_manager.get()
        value = await client.get(key)
        if value is None:
            return None
        return json.loads(value)
    except Exception as e:
        logger.warning("Cache get failed for key %s: %s", key, e)
        return None


async def update_cache(key: str, value: Any, ttl: int = 300) -> None:
    try:
        client = redis_manager.get()
        await client.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception as e:
        logger.warning("Cache update failed for key %s: %s", key, e)