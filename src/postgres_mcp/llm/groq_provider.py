"""
Groq LLM provider implementation.

This is the ONLY file in the codebase that imports the groq SDK
directly. Retry-with-backoff handles transient failures (rate limits,
brief network issues) without surfacing them as hard failures on the
first blip — but we still fail loudly after a few attempts rather than
retrying forever.
"""

import asyncio

from groq import AsyncGroq
from loguru import logger

from postgres_mcp.config import get_settings
from postgres_mcp.exceptions import LLMProviderError
from postgres_mcp.llm.base import LLMProvider

_MAX_RETRIES = 3
_BASE_DELAY_SECONDS = 1.0


class GroqProvider(LLMProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncGroq(api_key=settings.groq_api_key)
        self._model = settings.groq_model

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        last_error: Exception | None = None

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = await self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                )
                return response.choices[0].message.content
            except Exception as exc:
                last_error = exc
                logger.warning(f"Groq call failed (attempt {attempt}/{_MAX_RETRIES}): {exc}")
                if attempt < _MAX_RETRIES:
                    await asyncio.sleep(_BASE_DELAY_SECONDS * attempt)

        raise LLMProviderError(f"Groq call failed after {_MAX_RETRIES} attempts: {last_error}")