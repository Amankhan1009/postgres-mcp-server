"""
Schema service — orchestrates schema_repository calls and adds the
business rule that matters most here: never let a table name from an
MCP tool call go straight into f-string SQL.

Why this validation matters: count_rows() in the repository builds
its query with an f-string (SELECT COUNT(*) FROM {table_name}) because
table names cannot be parameterized with bind parameters in SQL — the
driver has no way to safely substitute an identifier the way it does
a value. The defense instead is a whitelist check here, BEFORE the
repository ever sees the input: table_name must already exist in
list_tables(). This is the same principle as parameterized queries,
applied to identifiers instead of values.
"""

from postgres_mcp.db.engine import get_session
from postgres_mcp.exceptions import PostgresMCPError
from postgres_mcp.repositories.schema_repository import SchemaRepository


class SchemaService:
    def __init__(self) -> None:
        self._repo = SchemaRepository()

    async def list_tables(self) -> list[str]:
        async with get_session() as session:
            return await self._repo.list_tables(session)

    async def _validate_table_exists(self, session, table_name: str) -> None:
        valid_tables = await self._repo.list_tables(session)
        if table_name not in valid_tables:
            raise PostgresMCPError(
                f"Table '{table_name}' does not exist. "
                f"Available tables: {', '.join(valid_tables)}"
            )

    async def describe_table(self, table_name: str) -> dict:
        async with get_session() as session:
            await self._validate_table_exists(session, table_name)
            columns = await self._repo.list_columns(session, table_name)
            foreign_keys = await self._repo.list_foreign_keys(session, table_name)
            return {"table_name": table_name, "columns": columns, "foreign_keys": foreign_keys}

    async def list_columns(self, table_name: str) -> list[dict]:
        async with get_session() as session:
            await self._validate_table_exists(session, table_name)
            return await self._repo.list_columns(session, table_name)

    async def count_rows(self, table_name: str) -> int:
        async with get_session() as session:
            await self._validate_table_exists(session, table_name)
            return await self._repo.count_rows(session, table_name)

    async def search_schema(self, keyword: str) -> list[dict]:
        async with get_session() as session:
            return await self._repo.search_schema(session, keyword)

    async def find_related_tables(self, table_name: str, max_depth: int = 2) -> dict:
        async with get_session() as session:
            await self._validate_table_exists(session, table_name)
            all_fks = await self._repo.list_all_foreign_keys(session)

        # Build an undirected adjacency map: a FK in either direction
        # counts as a relationship between the two tables.
        graph: dict[str, set[str]] = {}
        for fk in all_fks:
            graph.setdefault(fk["from_table"], set()).add(fk["to_table"])
            graph.setdefault(fk["to_table"], set()).add(fk["from_table"])

        visited = {table_name: 0}
        queue = [table_name]
        while queue:
            current = queue.pop(0)
            current_depth = visited[current]
            if current_depth >= max_depth:
                continue
            for neighbor in graph.get(current, set()):
                if neighbor not in visited:
                    visited[neighbor] = current_depth + 1
                    queue.append(neighbor)

        related = {table: depth for table, depth in visited.items() if table != table_name}
        return {"table_name": table_name, "related_tables": related}

    async def summarize_row_counts(self) -> dict[str, int]:
        async with get_session() as session:
            tables = await self._repo.list_tables(session)
            counts = {}
            for table in tables:
                if table == "alembic_version":
                    continue
                counts[table] = await self._repo.count_rows(session, table)
            return counts