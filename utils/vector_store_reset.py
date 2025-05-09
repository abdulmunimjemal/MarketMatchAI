"""
Utility module for resetting the vector store.
This is in a separate module to avoid circular imports.
"""

import os
import logging

logger = logging.getLogger(__name__)

# Keep track of vector store singleton
_vector_store = None

def reset_vector_store():
    """Reset the vector store singleton to force reinitialization"""
    global _vector_store
    _vector_store = None
    logger.info("Vector store reset, will be reinitialized on next access")

def get_vector_store_instance():
    """Get the vector store instance or None if not initialized"""
    global _vector_store
    return _vector_store

def set_vector_store_instance(instance):
    """Set the vector store instance"""
    global _vector_store
    _vector_store = instance