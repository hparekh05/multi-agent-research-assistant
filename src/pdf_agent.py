from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
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
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(all_docs)
    
    vectorstore = Chroma.from_documents(chunks, embeddings)
    results = vectorstore.similarity_search(query, k=5)
    
    content = "\n\n".join([f"From {doc.metadata.get('source', 'PDF')}:\n{doc.page_content}" for doc in results])
    
    return {
        "content": content,
        "sources": sources,
        "agent": "pdf"
    }