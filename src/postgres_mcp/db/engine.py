"""
Async SQLAlchemy engine and session factory.

Why this file exists:
This is the ONLY place in the codebase that knows about connection
pooling and engine configuration. Every repository gets a session
through `get_session()` rather than creating its own engine — this
guarantees we have exactly one pool for the whole app, which is what
lets connection pooling actually work (a new engine per request would
defeat the purpose).

Concepts:
- create_async_engine: builds a connection pool factory, doesn't
  connect immediately.
- pool_size / max_overflow: pool_size is how many connections stay
  open and ready; max_overflow is how many extra it can open under
  burst load before requests start queueing.
- pool_pre_ping: before handing out a pooled connection, SQLAlchemy
  sends a lightweight check. Neon can idle-timeout connections, so
  without this you'd occasionally get "connection closed" errors on
  a connection that looked fine in the pool.
- async_sessionmaker: a factory for AsyncSession objects, bound to
  our engine.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from postgres_mcp.config import get_settings
from postgres_mcp.exceptions import DatabaseConnectionError

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=1800,  # recycle connections every 30 min
            echo=(settings.environment == "development"),
        )
        logger.info("Database engine created")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
        )
    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """
    Yields a session and guarantees rollback on error, commit on success.

    Repositories use this as:
        async with get_session() as session:
            ...
    so no repository ever manually manages transaction boundaries.
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error(f"Session rolled back due to: {exc}")
            raise DatabaseConnectionError(str(exc)) from exc