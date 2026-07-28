"""
Unit tests for sql_guard — the core SQL injection defense.

This is the highest-value test file in the project: sql_guard is
what stands between an AI client and arbitrary SQL execution. Every
bypass attempt we can think of should be a test case here.
"""

import pytest

from postgres_mcp.exceptions import UnsafeQueryError
from postgres_mcp.utils.sql_guard import enforce_row_limit, validate_select_only


class TestValidateSelectOnly:
    def test_accepts_simple_select(self):
        query = "SELECT * FROM employees"
        assert validate_select_only(query) == query

    def test_accepts_select_with_join(self):
        query = "SELECT e.name FROM employees e JOIN departments d ON e.department_id = d.id"
        assert validate_select_only(query) == query

    def test_rejects_delete(self):
        with pytest.raises(UnsafeQueryError, match="Only SELECT"):
            validate_select_only("DELETE FROM employees WHERE id = 1")

    def test_rejects_insert(self):
        with pytest.raises(UnsafeQueryError, match="Only SELECT"):
            validate_select_only("INSERT INTO employees (first_name) VALUES ('x')")

    def test_rejects_update(self):
        with pytest.raises(UnsafeQueryError, match="Only SELECT"):
            validate_select_only("UPDATE employees SET salary = 0")

    def test_rejects_drop_table(self):
        with pytest.raises(UnsafeQueryError, match="Only SELECT"):
            validate_select_only("DROP TABLE employees")

    def test_rejects_chained_statements(self):
        with pytest.raises(UnsafeQueryError, match="single SQL statement"):
            validate_select_only("SELECT * FROM employees; DROP TABLE employees;")

    def test_rejects_empty_query(self):
        with pytest.raises(UnsafeQueryError, match="empty"):
            validate_select_only("")

    def test_rejects_whitespace_only_query(self):
        with pytest.raises(UnsafeQueryError, match="empty"):
            validate_select_only("   ")

    def test_rejects_forbidden_function_pg_sleep(self):
        with pytest.raises(UnsafeQueryError, match="forbidden function"):
            validate_select_only("SELECT pg_sleep(10)")

    def test_rejects_forbidden_function_pg_read_file(self):
        with pytest.raises(UnsafeQueryError, match="forbidden function"):
            validate_select_only("SELECT pg_read_file('/etc/passwd')")

    def test_rejects_truncate(self):
        with pytest.raises(UnsafeQueryError, match="Only SELECT"):
            validate_select_only("TRUNCATE employees")

    def test_rejects_grant(self):
        with pytest.raises(UnsafeQueryError):
            validate_select_only("GRANT ALL ON employees TO public")

    def test_strips_trailing_semicolon(self):
        query = "SELECT * FROM employees;"
        result = validate_select_only(query)
        assert not result.endswith(";")


class TestEnforceRowLimit:
    def test_adds_limit_when_missing(self):
        result = enforce_row_limit("SELECT * FROM employees", max_rows=50)
        assert "LIMIT 50" in result

    def test_does_not_duplicate_existing_limit(self):
        query = "SELECT * FROM employees LIMIT 10"
        result = enforce_row_limit(query, max_rows=50)
        assert result.count("LIMIT") == 1