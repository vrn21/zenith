"""Entry point for the Banking MCP Server."""

from src.zenith.server import mcp


if __name__ == "__main__":
    mcp.run(transport="sse")
