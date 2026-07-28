"""
MCP server entrypoint.

This is the file you actually run to start the server. It creates the
FastMCP instance, registers every tool module, and starts listening
for MCP client connections over stdio (the standard transport for
local MCP servers used by Claude Desktop, Claude Code, etc.).
"""

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