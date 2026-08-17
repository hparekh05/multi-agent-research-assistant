from src.web_agent import web_search_agent
from src.pdf_agent import pdf_agent
from src.synthesizer import synthesizer_agent

def orchestrator(query: str, uploaded_files=None) -> dict:
    """
    Orchestrator agent that coordinates all other agents.
    Decides which agents to call and in what order.
    """
    
    print(f"Orchestrator received query: {query}")
    
    # Step 1: Run web search agent
    print("Running web search agent...")
    web_results = web_search_agent(query)
    
    # Step 2: Run PDF agent if files uploaded
    print("Running PDF agent...")
    pdf_results = pdf_agent(uploaded_files or [], query)
    
    # Step 3: Synthesizer combines everything
    print("Running synthesizer agent...")
    final_result = synthesizer_agent(query, web_results, pdf_results)
    
    return {
        "answer": final_result["answer"],
        "sources": final_result["sources"],
        "web_sources": final_result["web_sources"],
        "pdf_sources": final_result["pdf_sources"],
        "query": query
    }