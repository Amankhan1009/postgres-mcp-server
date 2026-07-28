"""
Query service — the only entry point for running LLM/user-supplied
SQL. Ties sql_guard validation to query_repository execution, and
converts any raw database error into our own QueryExecutionError so
internal details (stack traces, driver internals) never reach the
MCP client directly.
"""

from postgres_mcp.db.engine import get_session
from postgres_mcp.exceptions import QueryExecutionError
from postgres_mcp.repositories.query_repository import QueryRepository
from postgres_mcp.utils.sql_guard import enforce_row_limit, validate_select_only


class QueryService:
    def __init__(self) -> None:
        self._repo = QueryRepository()

    async def execute_select(self, raw_query: str, max_rows: int = 100) -> list[dict]:
        validated_query = validate_select_only(raw_query)
        limited_query = enforce_row_limit(validated_query, max_rows)

        async with get_session() as session:
            try:
                return await self._repo.execute_select(session, limited_query)
            except Exception as exc:
                raise QueryExecutionError(f"Query execution failed: {exc}") from exc