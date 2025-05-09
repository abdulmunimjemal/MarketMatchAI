import os
import logging

logger = logging.getLogger(__name__)

def set_vector_store_type(store_type):
    """
    Set the vector store type to use (pinecone or faiss)
    This is a utility function that can be used to switch between vector stores
    """
    # Validate the input
    if store_type not in ['pinecone', 'faiss']:
        logger.error(f"Invalid vector store type: {store_type}. Must be 'pinecone' or 'faiss'")
        return False
    
    # Set the environment variable
    os.environ["VECTOR_STORE_TYPE"] = store_type
    logger.info(f"Vector store type set to: {store_type}")
    
    # Import here to avoid circular imports
    import utils.vector_store
    utils.vector_store.reset_vector_store()
    
    return True

def get_vector_store_type():
    """
    Get the current vector store type
    """
    return os.environ.get("VECTOR_STORE_TYPE", "faiss").lower()

def is_pinecone_available():
    """
    Check if Pinecone is available (credentials are set)
    """
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    pinecone_environment = os.environ.get("PINECONE_ENVIRONMENT")
    
    if not pinecone_api_key or not pinecone_environment:
        logger.warning("Pinecone credentials not found")
        return False
    
    return True