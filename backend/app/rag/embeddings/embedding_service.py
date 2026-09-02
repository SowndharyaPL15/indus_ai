import logging

logger = logging.getLogger(__name__)

_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        try:
            from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
            _embeddings = FastEmbedEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            logger.info("Initialized FastEmbedEmbeddings (all-MiniLM-L6-v2) successfully.")
        except Exception as e:
            logger.warning(f"FastEmbedEmbeddings initialization failed ({e}), falling back to HuggingFaceEmbeddings.")
            from langchain_community.embeddings import HuggingFaceEmbeddings
            _embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _embeddings

