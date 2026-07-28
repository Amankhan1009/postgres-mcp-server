"""
Unit tests for SchemaService using a mocked repository — no real
database connection needed, so these run fast and don't require
Neon credentials in CI.
"""

from unittest.mock import AsyncMock, patch

import pytest

from postgres_mcp.exceptions import PostgresMCPError
from postgres_mcp.services.schema_service import SchemaService


@pytest.fixture
def service():
    return SchemaService()


class TestDescribeTable:
    async def test_raises_for_nonexistent_table(self, service):
        with patch.object(service, "_repo") as mock_repo:
            mock_repo.list_tables = AsyncMock(return_value=["employees", "clients"])
            with patch("postgres_mcp.services.schema_service.get_session") as mock_get_session:
                mock_get_session.return_value.__aenter__.return_value = AsyncMock()
                with pytest.raises(PostgresMCPError, match="does not exist"):
                    await service.describe_table("nonexistent_table")

    async def test_succeeds_for_existing_table(self, service):
        with patch.object(service, "_repo") as mock_repo:
            mock_repo.list_tables = AsyncMock(return_value=["employees"])
            mock_repo.list_columns = AsyncMock(return_value=[{"column_name": "id"}])
            mock_repo.list_foreign_keys = AsyncMock(return_value=[])
            with patch("postgres_mcp.services.schema_service.get_session") as mock_get_session:
                mock_get_session.return_value.__aenter__.return_value = AsyncMock()
                result = await service.describe_table("employees")
                assert result["table_name"] == "employees"