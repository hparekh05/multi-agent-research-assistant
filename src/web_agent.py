from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

def web_search_agent(query: str) -> dict:
    """Agent that searches the web for information."""
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    results = client.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )
    
    sources = []
    content = []
    
    for result in results.get("results", []):
        sources.append(result.get("url", ""))
        content.append(f"Source: {result.get('url', '')}\n{result.get('content', '')}")
    
    return {
        "content": "\n\n".join(content),
        "sources": sources,
        "agent": "web_search"
    }
    