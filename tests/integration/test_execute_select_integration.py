"""
Integration test for execute_select against the real Neon database.
Uses the actual seeded data — read-only, so no cleanup/rollback of
data is needed (the read-only transaction guarantees this at the
Postgres level too).

Requires real DATABASE_URL in .env — these are skipped in
environments without database access via the marker below.
"""

import pytest

from postgres_mcp.services.query_service import QueryService

pytestmark = pytest.mark.integration


class TestExecuteSelectIntegration:
    async def test_real_query_against_seeded_data(self):
        service = QueryService()
        rows = await service.execute_select("SELECT COUNT(*) as total FROM employees")
        assert rows[0]["total"] == 25

    async def test_real_query_with_join(self):
        service = QueryService()
        rows = await service.execute_select(
            "SELECT e.first_name, d.name FROM employees e "
            "JOIN departments d ON e.department_id = d.id "
            "WHERE d.name = 'Engineering'"
        )
        assert len(rows) == 8  # Engineering has 8 employees in seed data