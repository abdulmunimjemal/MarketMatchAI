import logging

logger = logging.getLogger(__name__)

# Import from config module to avoid duplication
from utils.config import set_vector_store_type as config_set_vector_store_type
from utils.config import get_vector_store_type as config_get_vector_store_type
from utils.config import is_pinecone_available as config_is_pinecone_available

def set_vector_store_type(store_type):
    """
    Set the vector store type to use (pinecone or faiss)
    This is a utility function that can be used to switch between vector stores
    """
    # Use the main config module to set the vector store type
    result = config_set_vector_store_type(store_type)
    
    if result:
        # Import here to avoid circular imports
        from utils.vector_store_reset import reset_vector_store
        reset_vector_store()
    
    return result

def get_vector_store_type():
    """
    Get the current vector store type
    """
    return config_get_vector_store_type()

def is_pinecone_available():
    """
    Check if Pinecone is available (credentials are set)
    """
    return config_is_pinecone_available()