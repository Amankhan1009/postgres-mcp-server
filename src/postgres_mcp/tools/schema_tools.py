"""
Schema introspection MCP tools.

Each function here is registered as an MCP tool on the server instance
passed in via register(). Docstrings are not just documentation —
they're what the connected AI client reads to decide when and how to
call each tool, so they're written for an LLM audience: clear purpose,
clear parameters, no internal jargon.
"""

from fastmcp import FastMCP

from postgres_mcp.services.schema_service import SchemaService

_service = SchemaService()


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_tables() -> list[str]:
        """List all tables in the connected PostgreSQL database."""
        return await _service.list_tables()

    @mcp.tool()
    async def describe_table(table_name: str) -> dict:
        """
        Describe a table's structure: its columns (name, type,
        nullability, default) and its foreign key relationships.

        Args:
            table_name: Exact name of the table, e.g. "employees".
        """
        return await _service.describe_table(table_name)

    @mcp.tool()
    async def list_columns(table_name: str) -> list[dict]:
        """
        List just the columns of a table (name, data type, nullable,
        default value), without foreign key info.

        Args:
            table_name: Exact name of the table, e.g. "invoices".
        """
        return await _service.list_columns(table_name)

    @mcp.tool()
    async def count_rows(table_name: str) -> int:
        """
        Count the number of rows currently in a table.

        Args:
            table_name: Exact name of the table, e.g. "clients".
        """
        return await _service.count_rows(table_name)

    @mcp.tool()
    async def search_schema(keyword: str) -> list[dict]:
        """
        Search all table and column names in the database for a
        keyword. Useful when you don't know the exact table/column
        name but know roughly what you're looking for (e.g. "email").

        Args:
            keyword: Partial text to search for, case-insensitive.
        """
        return await _service.search_schema(keyword)

    @mcp.tool()
    async def find_related_tables(table_name: str, max_depth: int = 2) -> dict:
        """
        Find tables related to the given table, directly or indirectly,
        by traversing foreign key relationships. Depth 1 means directly
        connected via a FK; depth 2 means connected through one
        intermediate table, and so on.

        Args:
            table_name: Exact name of the table, e.g. "employees".
            max_depth: How many relationship hops to search (default 2).
        """
        return await _service.find_related_tables(table_name, max_depth)