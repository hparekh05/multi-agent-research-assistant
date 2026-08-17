from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

def synthesizer_agent(query: str, web_results: dict, pdf_results: dict) -> dict:
    """Agent that synthesizes results from web and PDF agents into a final answer."""
    
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=2000
    )
    
    context = f"""
WEB SEARCH RESULTS:
{web_results.get('content', 'No web results found.')}

PDF DOCUMENT RESULTS:
{pdf_results.get('content', 'No PDF results found.')}
"""
    
    messages = [
        SystemMessage(content="""You are a research assistant that synthesizes information from multiple sources.
        Always:
        - Clearly attribute information to its source (web or document)
        - Structure your response with clear sections
        - Highlight key findings
        - Note any conflicting information between sources
        - End with a concise summary"""),
        HumanMessage(content=f"Research question: {query}\n\nContext:\n{context}")
    ]
    
    response = llm.invoke(messages)
    
    all_sources = web_results.get('sources', []) + pdf_results.get('sources', [])
    
    return {
        "answer": response.content,
        "sources": all_sources,
        "web_sources": web_results.get('sources', []),
        "pdf_sources": pdf_results.get('sources', [])
    }