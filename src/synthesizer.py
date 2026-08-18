from langchain_anthropic import ChatAnthropic
# LangChain's wrapper for Claude API
from langchain_core.messages import HumanMessage, SystemMessage
# Two types of messages:
# SystemMessage = instructions you give Claude ("you are a research assistant...")
# HumanMessage = the actual question/content
from dotenv import load_dotenv
import os

load_dotenv()

def synthesizer_agent(query: str, web_results: dict, pdf_results: dict) -> dict:
    """Agent that synthesizes results from web and PDF agents into a final answer."""
    
    try:
        llm = ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            max_tokens=2500  # Increased for more detailed responses
        )
        
        context = f"""
WEB SEARCH RESULTS:
{web_results.get('content', 'No web results found.')}

PDF DOCUMENT RESULTS:
{pdf_results.get('content', 'No PDF results found.')}
"""
        
        messages = [
            SystemMessage(content="""You are an expert research analyst that synthesizes 
information from multiple sources into clear, structured reports.

Your responses must:
- Start with a brief executive summary (2-3 sentences)
- Use clear sections with emoji headers for readability
- Explicitly attribute claims to their source (web or document)
- Highlight conflicting information between sources when found
- Include a Key Takeaways section at the end
- Be factual and avoid speculation beyond what sources support

Never fabricate information. If sources don't cover something, say so clearly."""),
            HumanMessage(content=f"Research question: {query}\n\nResearch context:\n{context}")
        ]
        
        response = llm.invoke(messages)
        
        all_sources = web_results.get('sources', []) + pdf_results.get('sources', [])
        
        return {
            "answer": response.content,
            "sources": all_sources,
            "web_sources": web_results.get('sources', []),
            "pdf_sources": pdf_results.get('sources', [])
        }
    
    except Exception as e:
        print(f"Synthesis failed: {e}")
        return {
            "answer": "I encountered an error synthesizing the research. Please try again.",
            "sources": [],
            "web_sources": [],
            "pdf_sources": []
        }