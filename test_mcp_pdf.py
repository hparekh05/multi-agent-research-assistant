
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROJECT_ROOT = Path(__file__).resolve().parent
PDF_PATH = Path(
    "/Users/hiyaparekh/Downloads/HiyaParekhResume.pdf"
)


async def main():
    if not PDF_PATH.is_file():
        print(f"PDF not found: {PDF_PATH}")
        return

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.mcp_server"],
        cwd=str(PROJECT_ROOT),
    )

    async with stdio_client(server_params) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available MCP tools:")
            for tool in tools.tools:
                print(f"- {tool.name}")

            print("\nTesting PDF search...")

            result = await session.call_tool(
                "search_documents",
                {
                    "query": "What are Hiya's technical skills and AI project experience?",
                    "pdf_path": str(PDF_PATH),
                },
            )

            for item in result.content:
                if hasattr(item, "text"):
                    try:
                        response = json.loads(item.text)
                        print("\n=== PDF SEARCH RESULT ===")
                        print("Error:", response.get("error"))
                        print("Sources:", response.get("sources"))
                        print("Content:")
                        print(response.get("content"))
                    except json.JSONDecodeError:
                        print(item.text)


if __name__ == "__main__":
    asyncio.run(main())
