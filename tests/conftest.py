"""
Shared pytest fixtures.

Why centralize these: every test file needing a mock session or fake
LLM provider imports from here instead of redefining setup — keeps
test files focused on assertions, not boilerplate.
"""

from unittest.mock import AsyncMock

import pytest

from postgres_mcp.llm.base import LLMProvider


class FakeLLMProvider(LLMProvider):
    """Returns a canned response instead of calling Groq — used to
    test services/tools without network calls or API costs."""

    def __init__(self, response: str = "fake llm response") -> None:
        self.response = response
        self.last_system_prompt: str | None = None
        self.last_user_prompt: str | None = None

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return self.response


@pytest.fixture
def fake_llm() -> FakeLLMProvider:
    return FakeLLMProvider()


@pytest.fixture
def mock_session():
    """A mock AsyncSession — repositories receive this instead of a
    real DB connection in unit tests."""
    session = AsyncMock()
    return session