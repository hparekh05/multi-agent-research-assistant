import streamlit as st
from src.orchestrator import orchestrator

st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Multi-Agent Research Assistant")
st.markdown("*Powered by Claude + Web Search + Document Analysis*")

# Sidebar for PDF upload
with st.sidebar:
    st.header("📄 Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDFs to include in research",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"{len(uploaded_files)} document(s) uploaded")
        for f in uploaded_files:
            st.write(f"• {f.name}")
    
    st.divider()
    st.markdown("**How it works:**")
    st.markdown("1. 🌐 Web Agent searches the internet")
    st.markdown("2. 📄 PDF Agent searches your documents")
    st.markdown("3. 🧠 Synthesizer combines everything")
    st.markdown("4. ✅ Get a sourced, structured answer")

# Main chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.write(f"• {source}")

# Chat input
if query := st.chat_input("Ask anything..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
    
    # Run agents
    with st.chat_message("assistant"):
        with st.spinner("Agents working..."):
            try:
                result = orchestrator(query, uploaded_files)
                
                st.markdown(result["answer"])
                
                # Show sources
                if result["sources"]:
                    with st.expander("📚 Sources"):
                        if result["web_sources"]:
                            st.markdown("**🌐 Web Sources:**")
                            for source in result["web_sources"]:
                                st.write(f"• {source}")
                        if result["pdf_sources"]:
                            st.markdown("**📄 Document Sources:**")
                            for source in result["pdf_sources"]:
                                st.write(f"• {source}")
                
                # Save to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"]
                })
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
st.divider()
st.caption("Multi-Agent Research Assistant | Built with LangChain, Claude, Tavily & ChromaDB")