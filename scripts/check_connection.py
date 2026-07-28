"""
Standalone sanity script — confirms we can actually reach Neon.

Not part of the MCP server itself; run manually to validate Milestone 1.
"""

import asyncio

from sqlalchemy import text

from postgres_mcp.db.engine import get_engine
from postgres_mcp.logging_config import configure_logging


async def main() -> None:
    configure_logging()
    engine = get_engine()
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT version();"))
        version = result.scalar_one()
        print(f"✅ Connected to Neon PostgreSQL successfully.\n{version}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())