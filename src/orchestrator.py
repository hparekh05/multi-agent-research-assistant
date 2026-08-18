from langgraph.graph import StateGraph, END
# StateGraph builds the agent workflow as a graph
# END is a special marker that says "stop here"
from langgraph.prebuilt import ToolNode
# Pre-built node that handles tool execution automatically
from langchain_anthropic import ChatAnthropic
from langchain.tools import tool
# Decorator that turns a Python function into a tool Claude can use
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import TypedDict, Annotated, Sequence, Optional
# Python typing tools for defining data structures
import operator
import os
from dotenv import load_dotenv
from src.web_agent import web_search_agent
from src.pdf_agent import pdf_agent as pdf_search

load_dotenv()

# Global storage for uploaded files
_uploaded_files = []

def set_uploaded_files(files):
    global _uploaded_files
    _uploaded_files = files if files else []

# Define state
class AgentState(TypedDict):
    messages: Annotated[Sequence, operator.add]
    sources: list

# Define tools
@tool
def search_web(query: str) -> str:
    """Search the web for current, real-time information about any topic."""
    results = web_search_agent(query)
    return results.get("content", "No results found.")

@tool
def search_pdfs(query: str) -> str:
    """Search uploaded PDF documents for relevant information."""
    global _uploaded_files
    if not _uploaded_files:
        return "No PDF documents have been uploaded."
    results = pdf_search(_uploaded_files, query)
    return results.get("content", "No relevant content found in documents.")

def create_agent():
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=2500
    )
    
    tools = [search_web, search_pdfs]
    llm_with_tools = llm.bind_tools(tools)
    tool_node = ToolNode(tools)
    
    def agent_node(state: AgentState):
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response], "sources": state.get("sources", [])}
    
    def should_continue(state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        
        # Safety limit — prevent infinite loops
        tool_call_count = sum(
            1 for m in messages 
            if hasattr(m, "tool_calls") and m.tool_calls
        )
        if tool_call_count >= 4:  # Max 4 tool calls per query
            return END
            
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", END: END}
    )
    graph.add_edge("tools", "agent")

    return graph.compile()

def orchestrator(query: str, uploaded_files=None, chat_history=None) -> dict:
    """Main orchestrator using LangGraph ReAct agent."""
    
    set_uploaded_files(uploaded_files)
    
    system_message = SystemMessage(content="""You are an expert research analyst with two specialized tools:

1. search_web: Search the internet for current, real-time information
2. search_pdfs: Search uploaded documents for relevant content

Your research strategy:
- For factual or current questions: always search the web first
- For document-specific questions: search PDFs first, then supplement with web
- For comprehensive research: use both tools and cross-reference findings
- Always cite where information came from
- Flag any contradictions between sources
- Structure responses with clear headers and a summary

Quality standards:
- Never guess — if you don't find it, say so
- Prefer recent sources for time-sensitive topics
- Distinguish between facts and analysis""")

    messages = [system_message]
    
    # Add chat history for memory
    if chat_history:
        for msg in chat_history[-6:]:  # Last 3 exchanges
            messages.append(msg)
    
    messages.append(HumanMessage(content=query))
    
    agent = create_agent()
    
    initial_state = {
        "messages": messages,
        "sources": []
    }
    
    result = agent.invoke(initial_state)
    
    # Extract answer
    final_message = result["messages"][-1]
    answer = final_message.content if hasattr(final_message, "content") else str(final_message)
    

   # Extract actual URLs from web agent
    from src.web_agent import get_last_sources
    actual_sources = get_last_sources()
    
    web_sources = [f"[{s['title']}]({s['url']})" for s in actual_sources]
    pdf_sources = []
    
    for message in result["messages"]:
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call.get("name") == "search_pdfs":
                    pdf_sources.append("PDF document search")
    
    return {
        "answer": answer,
        "sources": web_sources + pdf_sources,
        "web_sources": web_sources,
        "pdf_sources": pdf_sources,
        "query": query
    }