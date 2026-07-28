"""
Custom exception hierarchy.

Why: catching bare `Exception` everywhere hides bugs and leaks internal
details (e.g., raw asyncpg errors) to MCP clients. By defining our own
exceptions, each layer can raise something specific, and the MCP tool
layer can catch `PostgresMCPError` broadly while still knowing exactly
what went wrong for logging purposes.
"""


class PostgresMCPError(Exception):
    """Base exception for all application-specific errors."""


class DatabaseConnectionError(PostgresMCPError):
    """Raised when the database cannot be reached."""


class QueryExecutionError(PostgresMCPError):
    """Raised when a SQL query fails to execute."""


class UnsafeQueryError(PostgresMCPError):
    """Raised when a query fails safety validation (e.g., not a SELECT)."""


class LLMProviderError(PostgresMCPError):
    """Raised when the LLM provider fails or returns an unusable response."""