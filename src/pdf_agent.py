from langchain_community.document_loaders import PyPDFLoader
# Tool that reads PDF files and extracts text
from langchain_text_splitters import RecursiveCharacterTextSplitter
# Tool that cuts long text into smaller chunks
from langchain_community.vectorstores import Chroma
# ChromaDB — stores text as vectors (numbers) for semantic search
from langchain_community.embeddings import SentenceTransformerEmbeddings
# Converts text into vectors using a local HuggingFace model
import tempfile
import os

def pdf_agent(uploaded_files, query: str) -> dict:
    """Agent that searches uploaded PDFs for relevant information."""
    if not uploaded_files:
        return {
            "content": "No PDFs uploaded.",
            "sources": [],
            "agent": "pdf"
        }
    
    try:
        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        all_docs = []
        sources = []
        
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            
            loader = PyPDFLoader(tmp_path)
            pages = loader.load()
            sources.append(uploaded_file.name)
            all_docs.extend(pages)
            os.unlink(tmp_path)
        
        # chunk_size=800 for more precise retrieval
        # chunk_overlap=150 to preserve context at boundaries
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
        chunks = splitter.split_documents(all_docs)
        
        vectorstore = Chroma.from_documents(chunks, embeddings)
        results = vectorstore.similarity_search(query, k=4)
        
        content = "\n\n".join([
            f"From {doc.metadata.get('source', 'PDF')} (page {doc.metadata.get('page', '?')}):\n{doc.page_content}"
            for doc in results
        ])
        
        return {
            "content": content,
            "sources": sources,
            "agent": "pdf"
        }
    
    except Exception as e:
        print(f"PDF search failed: {e}")
        return {
            "content": "PDF search encountered an error. Please try re-uploading your document.",
            "sources": [],
            "agent": "pdf"
        }