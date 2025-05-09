"""
Configuration module for the RAG system.
This module contains configuration variables and functions.
"""

import os
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# Vector store configuration
VECTOR_STORE_TYPE_KEY = "VECTOR_STORE_TYPE"
DEFAULT_VECTOR_STORE_TYPE = "faiss"
PINECONE_INDEX_NAME = "marketmatch"

# Configuration file path
CONFIG_FILE = Path("config.json")

def _load_config():
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
    return {}

def _save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")
        return False

def get_vector_store_type():
    """Get the configured vector store type"""
    # Check environment variable first
    env_type = os.environ.get(VECTOR_STORE_TYPE_KEY)
    if env_type:
        return env_type.lower()
    
    # Fall back to config file
    config = _load_config()
    if VECTOR_STORE_TYPE_KEY in config:
        return config[VECTOR_STORE_TYPE_KEY].lower()
    
    # Default
    return DEFAULT_VECTOR_STORE_TYPE

def set_vector_store_type(store_type):
    """Set the vector store type in both environment variables and config file"""
    if store_type not in ['pinecone', 'faiss']:
        logger.error(f"Invalid vector store type: {store_type}. Must be 'pinecone' or 'faiss'")
        return False
    
    # Set in environment
    os.environ[VECTOR_STORE_TYPE_KEY] = store_type
    
    # Set in config file
    config = _load_config()
    config[VECTOR_STORE_TYPE_KEY] = store_type
    success = _save_config(config)
    
    logger.info(f"Vector store type set to: {store_type}")
    return success

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