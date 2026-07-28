"""
Unit tests for InsightService using a fake LLM provider — verifies
prompt construction and response handling without real Groq calls.
"""

from unittest.mock import AsyncMock, patch

import pytest

from postgres_mcp.services.insight_service import InsightService


@pytest.fixture
def service(fake_llm):
    svc = InsightService(llm=fake_llm)
    return svc


class TestGenerateSql:
    async def test_returns_llm_response(self, service, fake_llm):
        with patch.object(service._schema_service, "list_tables", AsyncMock(return_value=[])):
            fake_llm.response = "SELECT * FROM employees"
            result = await service.generate_sql("show me all employees")
            assert result == "SELECT * FROM employees"

    async def test_includes_question_in_prompt(self, service, fake_llm):
        with patch.object(service._schema_service, "list_tables", AsyncMock(return_value=[])):
            await service.generate_sql("show me all employees")
            assert "show me all employees" in fake_llm.last_user_prompt