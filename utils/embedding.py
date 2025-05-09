import os
import logging
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings

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
            _embedding_instance = OpenAIEmbeddings(
                api_key=openai_api_key,
                model="text-embedding-ada-002"
            )
        # If no OpenAI key, try to use Google's text-embedding model
        else:
            google_api_key = os.environ.get("GOOGLE_API_KEY")
            if google_api_key:
                logger.info("Using Google embeddings")
                from langchain.embeddings import GooglePalmEmbeddings
                _embedding_instance = GooglePalmEmbeddings(
                    google_api_key=google_api_key
                )
            # As a fallback, use a local HuggingFace model
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
