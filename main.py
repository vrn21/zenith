"""Entry point for the Banking MCP Server."""

import os

from src.zenith.server import mcp


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "80"))
    
    mcp.run(transport="sse", host=host, port=port)

