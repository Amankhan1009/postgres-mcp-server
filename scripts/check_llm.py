"""
Standalone sanity script — confirms the Groq provider actually works.
Not part of the MCP server; run manually to validate Milestone 7.
"""

import asyncio

from postgres_mcp.llm.groq_provider import GroqProvider
from postgres_mcp.logging_config import configure_logging


async def main() -> None:
    configure_logging()
    provider = GroqProvider()
    response = await provider.generate(
        system_prompt="You are a concise PostgreSQL expert.",
        user_prompt="In one sentence, why are indexes useful in PostgreSQL?",
    )
    print(f"✅ Groq responded:\n{response}")


if __name__ == "__main__":
    asyncio.run(main())