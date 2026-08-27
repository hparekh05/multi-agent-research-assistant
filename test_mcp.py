import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.mcp_server"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:

            await session.initialize()

            # 1. Ask MCP server what tools it has
            tools = await session.list_tools()

            print("\n=== MCP TOOLS ===")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # 2. Actually call the web search tool
            print("\n=== TESTING search_web ===")

            result = await session.call_tool(
                "search_web",
                {"query": "latest developments in AI agents"}
            )

            for content in result.content:
                print("\n=== MCP RESPONSE ===")
                print(content.text)


if __name__ == "__main__":
    asyncio.run(main())