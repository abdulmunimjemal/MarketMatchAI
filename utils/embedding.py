import os
import logging
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

# Singleton pattern for embeddings to avoid recreating them
_embedding_instance = None

def get_embeddings():
    """Get or create an embedding model instance"""
    global _embedding_instance
    
    if _embedding_instance is not None:
        return _embedding_instance
    
    try:
        # Try to use OpenAI embeddings if key is provided
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if openai_api_key:
            logger.info("Using OpenAI embeddings")
            # Use api_key parameter as it works correctly
            _embedding_instance = OpenAIEmbeddings(
                api_key=openai_api_key,
                model="text-embedding-ada-002"
            )
        # Fall back to HuggingFace
        else:
            logger.info("Using HuggingFace embeddings as fallback")
            _embedding_instance = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        
        return _embedding_instance
    
    except Exception as e:
        logger.error(f"Error initializing embeddings: {str(e)}")
        raise

def embed_text(text):
    """Generate embeddings for a piece of text"""
    embeddings = get_embeddings()
    return embeddings.embed_query(text)

def embed_documents(texts):
    """Generate embeddings for multiple documents"""
    embeddings = get_embeddings()
    return embeddings.embed_documents(texts)
