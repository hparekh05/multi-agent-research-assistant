from mcp.server.fastmcp import FastMCP
from src.web_agent import web_search_agent
import json

# Initialize MCP server using FastMCP (newer API)
mcp = FastMCP("research-assistant")

@mcp.tool()
def search_web(query: str) -> str:
    """Search the web for current, real-time information about any topic."""
    results = web_search_agent(query)
    return json.dumps({
        "content": results.get("content", ""),
        "sources": [s.get("url", "") for s in results.get("sources", [])]
    })

@mcp.tool()
def search_documents(query: str) -> str:
    """Search uploaded PDF documents for relevant information."""
    return "Document search available when PDFs are uploaded through the main interface."

if __name__ == "__main__":
    mcp.run()