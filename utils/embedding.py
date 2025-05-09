import os
import logging
import numpy as np
from typing import List
from langchain_community.embeddings import OpenAIEmbeddings, FakeEmbeddings
from langchain.embeddings.base import Embeddings

logger = logging.getLogger(__name__)

# Singleton pattern for embeddings to avoid recreating them
_embedding_instance = None

class SimpleEmbeddings(Embeddings):
    """Simple embeddings class that produces deterministic embeddings based on text hash"""
    
    def __init__(self, embedding_size=1536):
        self.embedding_size = embedding_size
    
    def _hash_text(self, text):
        """Create a simple hash of text within numpy's random seed range (0 to 2^32-1)"""
        import hashlib
        # Use only the first 8 characters of the hash and convert to int
        # This ensures the value is within the required range for np.random.seed
        return int(hashlib.md5(text.encode('utf-8')).hexdigest()[:8], 16)
    
    def _text_to_vector(self, text):
        """Convert text to a deterministic embedding vector"""
        # Use the hash of the text as a seed for random number generation
        np.random.seed(self._hash_text(text))
        # Generate a random vector and normalize it
        vec = np.random.rand(self.embedding_size)
        return vec / np.linalg.norm(vec)
    
    def embed_query(self, text: str) -> List[float]:
        """Generate an embedding for a single text"""
        return self._text_to_vector(text).tolist()
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return [self._text_to_vector(text).tolist() for text in texts]

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
        # Fall back to simple embeddings when OpenAI is not available
        else:
            logger.info("Using simple deterministic embeddings as fallback")
            _embedding_instance = SimpleEmbeddings(embedding_size=1536)
        
        return _embedding_instance
    
    except Exception as e:
        logger.error(f"Error initializing embeddings: {str(e)}")
        # Ultimate fallback to fake embeddings
        logger.info("Using fake embeddings as last resort")
        _embedding_instance = FakeEmbeddings(size=1536)
        return _embedding_instance

def embed_text(text):
    """Generate embeddings for a piece of text"""
    embeddings = get_embeddings()
    return embeddings.embed_query(text)

def embed_documents(texts):
    """Generate embeddings for multiple documents"""
    embeddings = get_embeddings()
    return embeddings.embed_documents(texts)
