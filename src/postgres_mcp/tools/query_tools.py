"""
Query execution MCP tool — the highest-risk tool in this project.
Every safeguard (single-statement check, forbidden keyword/function
check, read-only transaction, row limit) exists because this tool
runs SQL text an AI client supplies directly.
"""

from fastmcp import FastMCP

from postgres_mcp.services.query_service import QueryService

_service = QueryService()


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def execute_select(query: str) -> list[dict]:
        """
        Execute a read-only SELECT query against the database and
        return the resulting rows. Only SELECT statements are
        permitted — any INSERT, UPDATE, DELETE, DDL, or multi-statement
        query is rejected. Results are capped at 100 rows unless the
        query includes its own LIMIT clause.

        Args:
            query: A single SQL SELECT statement, e.g.
                   "SELECT * FROM employees WHERE department_id = 1".
        """
        return await _service.execute_select(query)