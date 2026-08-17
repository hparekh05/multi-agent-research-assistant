# 🔍 Multi-Agent Research Assistant

An AI-powered research assistant that orchestrates multiple specialized agents to answer complex questions using both web search and document analysis.

## 🏗️ Architecture

## ✨ Features

- 🌐 **Web Search Agent** — searches the internet in real time using Tavily
- 📄 **PDF Agent** — performs semantic search across uploaded documents using vector embeddings
- 🧠 **Synthesizer Agent** — uses Claude to combine and structure information from all sources
- 📚 **Source Attribution** — every answer cites exactly where information came from
- 💬 **Conversation Memory** — remembers context across follow-up questions
- ⚡ **Multi-source synthesis** — identifies conflicts between sources

## 🛠️ Tech Stack

- **LangChain** — agent orchestration and RAG pipeline
- **Anthropic Claude** — LLM for synthesis and reasoning
- **Tavily** — real-time web search API
- **ChromaDB** — vector database for document storage
- **Sentence Transformers** — local embeddings (HuggingFace)
- **Streamlit** — production UI
- **Python** — core language

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Anthropic API key
- Tavily API key (free at tavily.com)

### Installation

```bash
git clone https://github.com/hparekh05/multi-agent-research-assistant.git
cd multi-agent-research-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

## 💡 Use Cases

- Research synthesis across multiple sources
- Document Q&A with web augmentation
- Competitive intelligence gathering
- Literature review automation

## 🔮 Roadmap

- [ ] LangGraph ReAct agent with dynamic tool selection
- [ ] Streaming responses
- [ ] Conversation memory persistence
- [ ] Public deployment on Streamlit Cloud
