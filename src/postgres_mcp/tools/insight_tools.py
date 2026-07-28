"""
LLM-powered MCP tools: generate_sql, explain_query, optimize_query.

These combine PostgreSQL schema data with Groq reasoning — the
"AI Database Assistant" behavior described in the project's original
objective, as opposed to a plain SQL executor.
"""

from fastmcp import FastMCP

from postgres_mcp.services.insight_service import InsightService
from postgres_mcp.services.query_service import QueryService


_service = InsightService()
_query_service = QueryService()

def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def generate_sql(question: str) -> str:
        """
        Generate a SQL SELECT query from a natural-language question,
        grounded in the actual database schema. Returns SQL text only —
        does not execute it. Review the query (or pass it to
        execute_select) before running it.

        Args:
            question: A natural-language question about the data, e.g.
                       "which clients have unpaid invoices over 20000?"
        """
        return await _service.generate_sql(question)

    @mcp.tool()
    async def explain_query(query: str) -> str:
        """
        Explain what a SQL query does in plain language.

        Args:
            query: The SQL query to explain.
        """
        return await _service.explain_query(query)

    @mcp.tool()
    async def optimize_query(query: str) -> str:
        """
        Suggest performance optimizations for a SQL query, considering
        the actual schema (indexes, relationships, etc).

        Args:
            query: The SQL query to analyze for optimization opportunities.
        """
        return await _service.optimize_query(query)

    @mcp.tool()
    async def summarize_database() -> str:
        """
        Generate a concise executive overview of the entire database:
        what kind of business it represents, its scale, and anything
        notable about its structure.
        """
        return await _service.summarize_database()

    @mcp.tool()
    async def business_insights(question: str) -> str:
        """
        Answer a free-form business question by generating and running
        the appropriate SQL query, then interpreting the results in
        plain language. Combines real database data with LLM reasoning.

        Args:
            question: A business question, e.g. "which department has
                       the highest average salary?" or "what's our total
                       unpaid invoice amount by client?"
        """
        return await _service.business_insights(question, _query_service)

    