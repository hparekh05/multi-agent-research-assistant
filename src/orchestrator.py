from langgraph.graph import StateGraph, END
# StateGraph builds the agent workflow as a graph
# END is a special marker that says "stop here"
from langgraph.prebuilt import ToolNode
# Pre-built node that handles tool execution automatically
from langchain_anthropic import ChatAnthropic
from langchain.tools import tool
# Decorator that turns a Python function into a tool Claude can use
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import TypedDict, Annotated, Sequence
import operator
import os
import tempfile

from dotenv import load_dotenv

from src.mcp_client import (
    search_web_mcp,
    search_documents_mcp
)

load_dotenv()

# Global storage for uploaded files
_uploaded_files = []


def set_uploaded_files(files):
    global _uploaded_files
    _uploaded_files = files if files else []


class AgentState(TypedDict):
    messages: Annotated[Sequence, operator.add]
    sources: list


@tool
def search_web(query: str) -> str:
    """
    Search the web for current, real-time information through MCP.
    """
    return search_web_mcp(query)


@tool
def search_pdfs(query: str) -> str:
    """
    Search uploaded PDF documents through MCP.
    """

    global _uploaded_files

    if not _uploaded_files:
        return "No PDF documents have been uploaded."

    results = []

    for uploaded_file in _uploaded_files:

        # Save Streamlit UploadedFile to a temporary PDF
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:

            tmp.write(uploaded_file.getvalue())
            pdf_path = tmp.name

        try:
            result = search_documents_mcp(
                query=query,
                pdf_path=pdf_path
            )

            results.append(
                f"Document: {uploaded_file.name}\n{result}"
            )

        finally:
            # Delete temporary PDF
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

    return "\n\n".join(results)


def create_agent():

    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=2500
    )

    tools = [
        search_web,
        search_pdfs
    ]

    llm_with_tools = llm.bind_tools(tools)

    tool_node = ToolNode(tools)

    def agent_node(state: AgentState):

        messages = state["messages"]

        response = llm_with_tools.invoke(messages)

        return {
            "messages": [response],
            "sources": state.get("sources", [])
        }

    def should_continue(state: AgentState):

        messages = state["messages"]

        last_message = messages[-1]

        # Prevent infinite tool loops
        tool_call_count = sum(
            1
            for message in messages
            if hasattr(message, "tool_calls")
            and message.tool_calls
        )

        if tool_call_count >= 4:
            return END

        if (
            hasattr(last_message, "tool_calls")
            and last_message.tool_calls
        ):
            return "tools"

        return END

    graph = StateGraph(AgentState)

    graph.add_node(
        "agent",
        agent_node
    )

    graph.add_node(
        "tools",
        tool_node
    )

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )

    graph.add_edge(
        "tools",
        "agent"
    )

    return graph.compile()


def orchestrator(
    query: str,
    uploaded_files=None,
    chat_history=None
) -> dict:

    """
    Main research orchestrator.

    The LangGraph agent uses MCP-powered tools
    for web and PDF research.
    """

    set_uploaded_files(uploaded_files)

    system_message = SystemMessage(
        content="""
You are an expert research analyst.

You have access to two research tools through
the Model Context Protocol (MCP):

1. search_web
   Search the internet for current information.

2. search_pdfs
   Search uploaded PDF documents.

Research strategy:

- For factual or current questions, search the web first.
- For document-specific questions, search the PDFs.
- For comprehensive research, use both tools.
- Cross-reference information when possible.
- Never guess.
- Clearly distinguish facts from analysis.
- Cite sources whenever possible.
- Flag contradictions between sources.
- Give structured, useful answers.
"""
    )

    messages = [system_message]

    # Add recent conversation history
    if chat_history:

        for msg in chat_history[-6:]:
            messages.append(msg)

    messages.append(
        HumanMessage(content=query)
    )

    agent = create_agent()

    initial_state = {
        "messages": messages,
        "sources": []
    }

    result = agent.invoke(initial_state)

    # Get final answer
    final_message = result["messages"][-1]

    answer = (
        final_message.content
        if hasattr(final_message, "content")
        else str(final_message)
    )

    return {
        "answer": answer,
        "sources": [],
        "web_sources": [],
        "pdf_sources": [],
        "query": query
    }