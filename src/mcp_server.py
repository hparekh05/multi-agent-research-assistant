from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

import asyncio
import json
import sys
import os

from src.web_agent import web_search_agent
from src.pdf_agent import pdf_agent


# Create MCP server
app = Server("research-assistant")

# Store PDFs provided by the application
_uploaded_files = []


def set_uploaded_files(files):
    """Store uploaded PDFs so the MCP PDF tool can search them."""
    global _uploaded_files
    _uploaded_files = files if files else []


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Tell MCP clients which tools are available."""

    return [
        Tool(
            name="search_web",
            description="Search the web for current, real-time information.",
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
            description="Search an uploaded PDF document for relevant information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question to search for in the PDF"
                     },
                    "pdf_path": {
                        "type": "string",
                        "description": "Absolute path to the PDF file"
                     }
                },
                "required": ["query", "pdf_path"]
        }
    )
]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    query = arguments.get("query", "")    

    if name == "search_web":

        results = web_search_agent(query)

        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "content": results.get("content", ""),
                    "sources": [
                        s.get("url", "")
                        for s in results.get("sources", [])
                    ]
                })
            )
        ]


    # PDF SEARCH
    elif name == "search_documents":
        query = arguments.get("query", "")
        pdf_path = arguments.get("pdf_path", "")
        
        if not pdf_path:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "content": "No PDF path was provided.",
                        "sources": []
                    })
                )
            ]

        try:
            # Create a PDF-compatible file object
            with open(pdf_path, "rb") as f:
                class PDFFile:
                    def __init__(self, file_object, filename):
                        self.file_object = file_object
                        self.name = filename
                    
                    def read(self):
                        return self.file_object.read()

                pdf_file = PDFFile(
                    f,
                    os.path.basename(pdf_path)
                )

                results = pdf_agent(
                    [pdf_file],
                    query
                )

            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "content": results.get("content", ""),
                        "sources": results.get("sources", [])
                    })
                )
            ]

        except Exception as e:
            print(
                f"PDF MCP search failed: {e}",
                file=sys.stderr
            )
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "content": f"PDF search failed: {str(e)}",
                        "sources": []
                    })
                )
             ]

async def main():

    async with stdio_server() as (
        read_stream,
        write_stream
    ):

        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())