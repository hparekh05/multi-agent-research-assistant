from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio
import json
from src.web_agent import web_search_agent
from src.pdf_agent import pdf_agent

# Initialize MCP server
app = Server("research-assistant")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools in this MCP server."""
    return [
        Tool(
            name="search_web",
            description="Search the web for current, real-time information about any topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_documents",
            description="Search uploaded documents for relevant information using semantic search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for documents"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from MCP clients."""
    
    if name == "search_web":
        query = arguments.get("query", "")
        results = web_search_agent(query)
        return [TextContent(
            type="text",
            text=json.dumps({
                "content": results.get("content", ""),
                "sources": [s.get("url", "") for s in results.get("sources", [])]
            })
        )]
    
    elif name == "search_documents":
        query = arguments.get("query", "")
        # Return message if no docs uploaded
        return [TextContent(
            type="text",
            text="Document search available when PDFs are uploaded through the main interface."
        )]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())