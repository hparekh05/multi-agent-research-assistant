import streamlit as st
from src.orchestrator import orchestrator
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Multi-Agent Research Assistant")
st.markdown("*Powered by Claude + Web Search + Document Analysis*")

# Sidebar
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
    
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()
    
    st.divider()
    st.markdown("**How it works:**")
    st.markdown("1. 🌐 Web Agent searches the internet")
    st.markdown("2. 📄 PDF Agent searches your documents")
    st.markdown("3. 🧠 Claude reasons and synthesizes")
    st.markdown("4. ✅ Structured answer with sources")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("📚 Sources"):
                if message.get("web_sources"):
                    st.markdown("**🌐 Web Sources:**")
                    for source in message["web_sources"]:
                        st.markdown(f"• {source}")
                if message.get("pdf_sources"):
                    st.markdown("**📄 Document Sources:**")
                    for source in message["pdf_sources"]:
                        st.markdown(f"• {source}")

# Chat input
if query := st.chat_input("Ask anything..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.chat_history.append(HumanMessage(content=query))
    
    with st.chat_message("user"):
        st.markdown(query)
    
    with st.chat_message("assistant"):
        with st.spinner("🤖 Agents working..."):
            try:
                result = orchestrator(
                    query=query,
                    uploaded_files=uploaded_files,
                    chat_history=st.session_state.chat_history
                )
                
                st.markdown(result["answer"])
                
                if result["sources"]:
                    with st.expander("📚 Sources"):
                        if result["web_sources"]:
                            st.markdown("**🌐 Web Sources:**")
                            for source in result["web_sources"]:
                                st.markdown(f"• {source}")
                        if result["pdf_sources"]:
                            st.markdown("**📄 Document Sources:**")
                            for source in result["pdf_sources"]:
                                st.markdown(f"• {source}")
                
                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"],
                    "web_sources": result["web_sources"],
                    "pdf_sources": result["pdf_sources"]
                })
                st.session_state.chat_history.append(
                    AIMessage(content=result["answer"])
                )
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.divider()
st.caption("Multi-Agent Research Assistant")