# Multi-Agent Research Assistant

**Research across the web and your own documents, with AI-generated answers grounded in retrieved sources.**

A Python-based research assistant that combines LLM-powered reasoning, web search, and semantic PDF retrieval. Built with Claude, LangChain, MCP, and Streamlit, the project explores how AI agents can connect external tools and synthesize information into useful, source-backed responses.

## Run with Docker

```
cp .env.example .env    # then add your ANTHROPIC_API_KEY and TAVILY_API_KEY
docker compose up --build
```

Open http://localhost:8501. The first build takes several minutes and needs roughly 15 GB of free disk space.

## What It Does

**Explore the web**

Retrieve information from web searches and preserve source URLs so users can follow up on relevant material.

**Ask questions about PDFs**

Upload documents and search for semantically relevant passages instead of relying only on exact keyword matches.

**Connect tools through MCP**

Use the Model Context Protocol to expose web research and document retrieval as tools that the assistant can invoke.

**Generate grounded answers**

Combine retrieved information into a clear response, with available web links and document references displayed in the interface.

## How It Works

The application brings together three main parts:

| Component | Responsibility |
|---|---|
| Streamlit interface | Accept questions, manage uploaded PDFs, and display responses |
| Research orchestration | Coordinate the LLM and available research tools |
| MCP tools | Retrieve web information and search uploaded documents |

Retrieved information is passed into the answer-generation workflow. The application then presents the response alongside the source references collected during retrieval.

## Built With

- **Python** for application logic and integration
- **Anthropic Claude** for language understanding and answer generation
- **LangChain and LangGraph** for LLM and agent workflow components
- **Model Context Protocol (MCP)** for tool integration
- **Tavily** for web search
- **ChromaDB and Sentence Transformers** for vector-based document retrieval
- **Streamlit** for the interactive interface

## Run Locally

### Requirements

- Python 3.10 or later
- Anthropic API key
- Tavily API key

### 1. Get the project

```bash
git clone https://github.com/hparekh05/multi-agent-research-assistant.git
cd multi-agent-research-assistant
```

### 2. Set up Python

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 3. Configure your API keys

Create a `.env` file in the root directory:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Use your own API keys in place of the placeholders. Keep `.env` private and out of version control.

### 4. Start the app

```bash
streamlit run app.py
```

Open the local address printed in the terminal.

## Run the MCP Tests

With your virtual environment activated, run:

```bash
python test_mcp.py
python test_mcp_client.py
python test_mcp_pdf.py
```

The tests exercise MCP tool discovery, client-server communication, and PDF search. External-service tests require valid credentials and network access.

## Engineering Focus

This project brings together several practical AI engineering concepts:

- Connecting LLM applications to external tools
- Retrieving relevant information from unstructured documents
- Separating tool execution from answer generation
- Returning source references with generated responses
- Building an interactive interface for research workflows

## Future Directions

- Improve PDF page-level citation accuracy
- Evaluate retrieval relevance and answer grounding
- Add automated tests for orchestration and error handling
- Support persistent research sessions
- Track latency, retrieval quality, and LLM usage

## Author

**Hiya Parekh**

[GitHub](https://github.com/hparekh05) · [Project Repository](https://github.com/hparekh05/multi-agent-research-assistant)

