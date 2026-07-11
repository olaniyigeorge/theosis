from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from pgvector.asyncpg import register_vector
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from .models.base import Base

from ..utils.logger import logger


class DatabaseManager:
    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None
        self._is_initialized = False

    def initialize(self, database_url: str, **engine_kwargs: object) -> None:
        if self._is_initialized:
            logger.warning("Database already initialized")
            return

        is_postgres = database_url.startswith("postgresql+asyncpg://")

        if is_postgres:
            engine_kwargs.setdefault("pool_pre_ping", True)
            engine_kwargs.setdefault("pool_size", 10)
            engine_kwargs.setdefault("max_overflow", 20)
            engine_kwargs.setdefault("pool_timeout", 30)
            engine_kwargs.setdefault("pool_recycle", 1800)

        self.engine = create_async_engine(
            database_url,
            future=True,
            **engine_kwargs,
        )

        if is_postgres:
            event.listen(
                self.engine.sync_engine,
                "connect",
                self._register_pgvector,
            )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=True,
        )
        self._is_initialized = True
        logger.info("Database initialized")

    @staticmethod
    def _register_pgvector(dbapi_connection, _connection_record) -> None:
        dbapi_connection.run_async(register_vector)

    async def create_tables(self) -> None:
        if self.engine is None:
            raise RuntimeError("Database not initialized")

        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()

        self.engine = None
        self.session_factory = None
        self._is_initialized = False
        logger.info("Database connections closed")

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        if self.session_factory is None:
            raise RuntimeError("Database not initialized")

        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


db_manager = DatabaseManager()