import asyncio
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _server_params() -> StdioServerParameters:
    """How to launch the MCP server subprocess.

    env is passed explicitly because the MCP stdio client only forwards a few variables
    (PATH, HOME, ...) by default. Without this, TAVILY_API_KEY and HF_HOME set through
    Docker or CI never reach the server, and web search / PDF search fail there.
    """
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.mcp_server"],
        cwd=str(PROJECT_ROOT),
        env=dict(os.environ),
    )


async def _call_mcp_tool(tool_name: str, arguments: dict):
    """Connect to the MCP server and call a tool."""

    server_params = _server_params()

    async with stdio_client(server_params) as (read_stream, write_stream):

        async with ClientSession(
            read_stream,
            write_stream
        ) as session:

            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=arguments
            )

            return result


def search_web_mcp(query: str) -> str:
    """Search the web through the MCP server."""

    result = asyncio.run(
        _call_mcp_tool(
            "search_web",
            {"query": query}
        )
    )

    if result.content:
        return result.content[0].text

    return "No results returned from MCP."


def search_documents_mcp(
    query: str,
    pdf_path: str
) -> str:
    """Search a PDF through the MCP server."""

    result = asyncio.run(
        _call_mcp_tool(
            "search_documents",
            {
                "query": query,
                "pdf_path": pdf_path
            }
        )
    )

    if result.content:
        return result.content[0].text

    return "No document results returned from MCP."


def list_mcp_tools():
    """Return the tools exposed by the MCP server."""

    async def _list():

        server_params = _server_params()

        async with stdio_client(server_params) as (
            read_stream,
            write_stream
        ):

            async with ClientSession(
                read_stream,
                write_stream
            ) as session:

                await session.initialize()

                result = await session.list_tools()

                return [
                    {
                        "name": tool.name,
                        "description": tool.description
                    }
                    for tool in result.tools
                ]

    return asyncio.run(_list())