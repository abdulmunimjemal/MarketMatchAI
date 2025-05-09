"""
Embeddings package for the RAG system.
"""

from app.rag.embeddings.base import get_embeddings, SimpleEmbeddings

__all__ = ['get_embeddings', 'SimpleEmbeddings']