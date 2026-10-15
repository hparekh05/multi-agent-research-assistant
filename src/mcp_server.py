
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from src.web_agent import web_search_agent

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings


mcp = FastMCP("research-assistant")


@mcp.tool()
def search_web(query: str) -> str:
    """Search the web for current information and return results with source URLs."""
    query = query.strip()

    if not query:
        return json.dumps({
            "content": "",
            "sources": [],
            "error": "Search query cannot be empty."
        })

    try:
        results = web_search_agent(query)

        if not isinstance(results, dict):
            raise ValueError("Unexpected response from web search agent.")

        content = results.get("content", "")
        raw_sources = results.get("sources", [])

        if not isinstance(raw_sources, list):
            raw_sources = []

        sources = [
            source["url"]
            for source in raw_sources
            if isinstance(source, dict)
            and isinstance(source.get("url"), str)
            and source["url"].strip()
        ]

        return json.dumps({
            "content": content if isinstance(content, str) else str(content),
            "sources": sources,
            "error": None
        })

    except Exception:
        return json.dumps({
            "content": "",
            "sources": [],
            "error": "Web search failed. Please try again."
        })


@mcp.tool()
def search_documents(query: str, pdf_path: str) -> str:
    """Search a PDF file for passages relevant to a query using semantic similarity."""

    query = query.strip()
    path = Path(pdf_path)

    if not query:
        return json.dumps({
            "content": "",
            "sources": [],
            "error": "Search query cannot be empty."
        })

    if not path.is_file() or path.suffix.lower() != ".pdf":
        return json.dumps({
            "content": "",
            "sources": [],
            "error": "The specified PDF file does not exist or is invalid."
        })

    try:
        # Load the PDF and extract its pages.
        pages = PyPDFLoader(str(path)).load()

        if not pages:
            return json.dumps({
                "content": "",
                "sources": [],
                "error": "No readable content was found in the PDF."
            })

        # Split the text into overlapping chunks for retrieval.
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150
        )
        chunks = splitter.split_documents(pages)

        if not chunks:
            return json.dumps({
                "content": "",
                "sources": [],
                "error": "No searchable text was found in the PDF."
            })

        # Embed the chunks and retrieve the most relevant passages.
        embeddings = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings
        )

        results = vectorstore.similarity_search(query, k=4)

        content = "\n\n".join(
            (
                f"Page {doc.metadata.get('page', 0) + 1}:\n"
                f"{doc.page_content}"
            )
            for doc in results
        )

        pages_found = sorted({
            doc.metadata.get("page", 0) + 1
            for doc in results
        })

        return json.dumps({
            "content": content,
            "sources": [
                f"{path.name}, page {page}"
                for page in pages_found
            ],
            "error": None
        })

    except Exception:
        # Return a safe error rather than exposing internal details.
        return json.dumps({
            "content": "",
            "sources": [],
            "error": "PDF search failed. Check the PDF and embedding dependencies."
        })


if __name__ == "__main__":
    mcp.run()
