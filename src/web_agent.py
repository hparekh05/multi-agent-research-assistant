from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

# Global storage for sources
_last_sources = []

def get_last_sources():
    return _last_sources

def web_search_agent(query: str) -> dict:
    """Agent that searches the web for information."""
    global _last_sources
    
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    results = client.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )
    
    sources = []
    content = []
    
    for result in results.get("results", []):
        url = result.get("url", "")
        title = result.get("title", url)
        text = result.get("content", "")
        
        if url:
            sources.append({"url": url, "title": title})
            content.append(f"Source: {title} ({url})\n{text}")
    
    _last_sources = sources
    
    return {
        "content": "\n\n".join(content),
        "sources": sources,
        "agent": "web_search"
    }
