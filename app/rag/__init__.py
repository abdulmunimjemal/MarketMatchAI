"""
RAG (Retrieval Augmented Generation) package for the AI Market Matching Tool.

This package provides the core RAG functionality for the application.
"""

from app.rag.api import (
    query_rag_system,
    add_document_to_rag,
    get_rag_system_status,
    reset_rag_system
)

__all__ = [
    'query_rag_system',
    'add_document_to_rag',
    'get_rag_system_status',
    'reset_rag_system'
]