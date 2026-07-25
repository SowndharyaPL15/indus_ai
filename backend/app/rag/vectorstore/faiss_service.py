import os
from langchain_community.vectorstores import FAISS
from app.rag.embeddings.embedding_service import get_embeddings

FAISS_INDEX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../storage/faiss"))

def get_faiss_index():
    embeddings = get_embeddings()
    if os.path.exists(os.path.join(FAISS_INDEX_PATH, "index.faiss")):
        return FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    return None

def add_documents_to_faiss(texts: list[str], metadatas: list[dict]):
    embeddings = get_embeddings()
    vectorstore = get_faiss_index()
    
    if vectorstore is None:
        vectorstore = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
    else:
        vectorstore.add_texts(texts, metadatas=metadatas)
        
    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    vectorstore.save_local(FAISS_INDEX_PATH)
