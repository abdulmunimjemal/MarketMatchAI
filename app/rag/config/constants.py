"""
Constants for the RAG system.

This module contains configuration constants for the RAG system.
"""

import os
from pathlib import Path

# Vector store configuration
VECTOR_STORE_TYPE = "chroma"
CHROMA_PERSIST_DIRECTORY = "chroma_db"
EMBEDDINGS_DIMENSION = 1536  # Default for most embedding models

# Ensure the chroma directory exists
Path(CHROMA_PERSIST_DIRECTORY).mkdir(exist_ok=True, parents=True)

# Document processing
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MAX_DOCUMENT_SIZE_MB = 10

# API Settings
EMBEDDING_API_TIMEOUT = 60  # seconds