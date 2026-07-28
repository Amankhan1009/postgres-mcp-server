"""
SQL safety validation for user/LLM-supplied queries.

Why this file is isolated: it has zero dependencies on the database
or MCP — pure string/parsing logic — which means we can unit test
every bypass attempt we can think of without spinning up Postgres.
This is exactly the kind of code that deserves the heaviest test
coverage in the whole project.
"""

import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import DDL, DML, Keyword

from postgres_mcp.exceptions import UnsafeQueryError

_FORBIDDEN_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "GRANT", "REVOKE", "COPY", "CALL", "EXECUTE",
    "VACUUM", "REINDEX", "REFRESH", "LOCK",
}

_FORBIDDEN_FUNCTIONS = {
    "pg_read_file", "pg_ls_dir", "pg_read_binary_file",
    "lo_import", "lo_export", "dblink", "pg_sleep",
}


def validate_select_only(raw_query: str) -> str:
    """
    Validates that raw_query is a single, safe SELECT statement.

    Raises UnsafeQueryError with a clear reason if not. Returns the
    stripped, validated query string on success.
    """
    query = raw_query.strip().rstrip(";")

    if not query:
        raise UnsafeQueryError("Query is empty.")

    parsed = sqlparse.parse(query)
    if len(parsed) != 1:
        raise UnsafeQueryError(
            "Only a single SQL statement is allowed (no chained statements)."
        )

    statement: Statement = parsed[0]
    statement_type = statement.get_type()

    if statement_type != "SELECT":
        raise UnsafeQueryError(
            f"Only SELECT statements are allowed. Detected: {statement_type}."
        )

    upper_query = query.upper()
    for keyword in _FORBIDDEN_KEYWORDS:
        # word-boundary-ish check to avoid false positives like a
        # column literally named "created_at" containing "CREATE"... 
        # sqlparse tokens are used below for the real check; this is
        # a fast pre-filter.
        if f" {keyword} " in f" {upper_query} " or upper_query.startswith(f"{keyword} "):
            raise UnsafeQueryError(f"Query contains a forbidden keyword: {keyword}.")

    for token in statement.flatten():
        if token.ttype in (DDL, DML) and token.value.upper() != "SELECT":
            raise UnsafeQueryError(f"Query contains a forbidden operation: {token.value}.")

    lowered = query.lower()
    for func in _FORBIDDEN_FUNCTIONS:
        if func in lowered:
            raise UnsafeQueryError(f"Query calls a forbidden function: {func}.")

    return query


def enforce_row_limit(query: str, max_rows: int = 100) -> str:
    """
    Appends a LIMIT clause if the query doesn't already have one,
    so a single execute_select call can't return unbounded rows into
    an LLM's context window.
    """
    if "limit" not in query.lower():
        query = f"{query} LIMIT {max_rows}"
    return query