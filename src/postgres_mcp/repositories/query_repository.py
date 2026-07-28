"""
Query execution repository.

By the time execute_select() here runs, sql_guard has already
validated the query's shape. This layer adds the final database-level
safety net: SET TRANSACTION READ ONLY means even a validation bug
upstream can't result in a write, because Postgres itself will reject
one at the transaction level.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class QueryRepository:
    async def execute_select(self, session: AsyncSession, query: str) -> list[dict]:
        await session.execute(text("SET TRANSACTION READ ONLY"))
        result = await session.execute(text(query))
        columns = list(result.keys())
        return [dict(zip(columns, row)) for row in result.fetchall()]