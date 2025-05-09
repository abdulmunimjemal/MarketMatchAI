"""
Configuration module for the RAG system.
This module contains configuration variables and functions.
"""

import os
import logging

logger = logging.getLogger(__name__)

# Vector store configuration
VECTOR_STORE_TYPE_KEY = "VECTOR_STORE_TYPE"
DEFAULT_VECTOR_STORE_TYPE = "faiss"
PINECONE_INDEX_NAME = "marketmatch"

def get_vector_store_type():
    """Get the configured vector store type"""
    return os.environ.get(VECTOR_STORE_TYPE_KEY, DEFAULT_VECTOR_STORE_TYPE).lower()

def set_vector_store_type(store_type):
    """Set the vector store type in environment variables"""
    if store_type not in ['pinecone', 'faiss']:
        logger.error(f"Invalid vector store type: {store_type}. Must be 'pinecone' or 'faiss'")
        return False
    
    os.environ[VECTOR_STORE_TYPE_KEY] = store_type
    logger.info(f"Vector store type set to: {store_type}")
    return True

def is_pinecone_available():
    """Check if Pinecone is available (credentials are set)"""
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    pinecone_environment = os.environ.get("PINECONE_ENVIRONMENT")
    
    if not pinecone_api_key or not pinecone_environment:
        logger.debug("Pinecone credentials not found")
        return False
    
    return True

def is_openai_available():
    """Check if OpenAI is available (API key is set)"""
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    
    if not openai_api_key:
        logger.debug("OpenAI API key not found")
        return False
    
    return True

def get_system_status():
    """Get the status of all system components"""
    return {
        "vector_store_type": get_vector_store_type(),
        "pinecone_available": is_pinecone_available(),
        "openai_available": is_openai_available(),
    }