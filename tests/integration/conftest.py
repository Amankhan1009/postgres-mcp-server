"""

Why this file exists: our db engine is a module-level singleton
(intentional — one shared pool per running app). But pytest-asyncio
gives each test function its own event loop, and an asyncpg
connection pool is bound to the loop that created it. Without
resetting the singleton between tests, test 2 would try to reuse a
pool tied to test 1's already-closed loop.

This autouse fixture disposes the engine after every integration
test, so the next test's get_engine() call lazily creates a fresh
engine bound to its own event loop.
"""

import pytest_asyncio

from postgres_mcp.db import engine as engine_module


@pytest_asyncio.fixture(autouse=True)
async def _reset_engine_between_tests():
    yield
    if engine_module._engine is not None:
        await engine_module._engine.dispose()
        engine_module._engine = None
        engine_module._session_factory = None