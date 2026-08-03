"""
MCP server entrypoint.
"""

import sys
from pathlib import Path

# Ensure the 'src' directory is on the import path, so `postgres_mcp` is
# importable as a package regardless of how this file is executed —
# whether via `python -m postgres_mcp.server` (works fine locally) or
# run directly as a script by a platform like FastMCP Cloud (which
# otherwise only adds this file's own folder to sys.path, not `src/`).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastmcp import FastMCP

from postgres_mcp.logging_config import configure_logging
from postgres_mcp.tools import insight_tools, query_tools, schema_tools

configure_logging()

mcp = FastMCP("postgres-mcp-server")

schema_tools.register(mcp)
query_tools.register(mcp)
insight_tools.register(mcp)

if __name__ == "__main__":
    mcp.run()