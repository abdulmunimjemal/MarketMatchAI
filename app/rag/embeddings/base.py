"""
Base embeddings module for the RAG system.

This module provides embedding functionality for the AI Market Matching Tool.
"""

import logging
import numpy as np
from typing import List
from langchain.embeddings.base import Embeddings
from app.rag.config.constants import EMBEDDINGS_DIMENSION

logger = logging.getLogger(__name__)

class SimpleEmbeddings(Embeddings):
    """Simple embeddings class that produces deterministic embeddings based on text hash"""
    
    def __init__(self, embedding_size=EMBEDDINGS_DIMENSION):
        """Initialize the SimpleEmbeddings class"""
        self.embedding_size = embedding_size
        logger.info("Using simple deterministic embeddings as fallback")
    
    def _hash_text(self, text):
        """Create a simple hash of text within numpy's random seed range (0 to 2^32-1)"""
        import hashlib
        return int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16) % (2**32 - 1)
    
    def _text_to_vector(self, text):
        """Convert text to a deterministic embedding vector"""
        # Set a deterministic seed based on the text hash
        np.random.seed(self._hash_text(text))
        
        # Generate a deterministic random vector
        vector = np.random.normal(size=self.embedding_size)
        
        # Normalize to unit length
        vector = vector / np.linalg.norm(vector)
        
        return vector.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """Generate an embedding for a single text"""
        return self._text_to_vector(text)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return [self._text_to_vector(text) for text in texts]

def get_embeddings() -> Embeddings:
    """Get or create an embedding model instance"""
    try:
        # Try to use OpenAI embeddings if key is available
        import os
        openai_key = os.environ.get("OPENAI_API_KEY")
        
        if openai_key:
            from langchain.embeddings import OpenAIEmbeddings
            logger.info("Using OpenAI embeddings")
            return OpenAIEmbeddings()
    except ImportError:
        logger.warning("OpenAI package not available, falling back to simple embeddings")
    except Exception as e:
        logger.warning(f"Error initializing OpenAI embeddings: {str(e)}, falling back to simple embeddings")
    
    # Fall back to simple embeddings
    return SimpleEmbeddings()