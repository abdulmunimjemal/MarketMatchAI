"""
Main API module for the RAG system.

This module provides the main entry points to the RAG system.
"""

import logging
import os
from typing import List, Dict, Any, Optional, Union
from langchain.docstore.document import Document as LangchainDocument

from app.rag.pipeline import get_rag_pipeline, reset_rag_pipeline
from app.rag.document_processors import process_file, process_text
from app.rag.vectorstores import get_chroma_store

logger = logging.getLogger(__name__)

def query_rag_system(question: str) -> Dict[str, Any]:
    """
    Query the RAG system with a question
    
    Args:
        question: The question to ask
        
    Returns:
        A dictionary containing the answer and sources
    """
    if not question:
        return {
            "query": "",
            "answer": "Please provide a question to answer.",
            "sources": [],
            "metadata": {
                "error": "Empty query",
                "timestamp": __import__("datetime").datetime.now().isoformat()
            }
        }
    
    try:
        pipeline = get_rag_pipeline()
        return pipeline.query(question)
    
    except Exception as e:
        logger.error(f"Error querying RAG system: {str(e)}")
        return {
            "query": question,
            "answer": "An error occurred while processing your query.",
            "sources": [],
            "metadata": {
                "error": str(e),
                "timestamp": __import__("datetime").datetime.now().isoformat()
            }
        }

def add_document_to_rag(
    document_content: Union[str, bytes],
    metadata: Optional[Dict[str, Any]] = None,
    file_path: Optional[str] = None,
    document_type: str = "text"
) -> Dict[str, Any]:
    """
    Add a document to the RAG system
    
    Args:
        document_content: The content of the document as text or bytes
        metadata: Additional metadata for the document
        file_path: Path to the file (if applicable)
        document_type: Type of document (text, file, etc.)
        
    Returns:
        Status of the document addition
    """
    try:
        # Process the document based on type
        if document_type == "file" and file_path:
            documents = process_file(file_path, metadata)
        elif document_type == "text" and isinstance(document_content, str):
            documents = process_text(document_content, metadata)
        else:
            return {
                "success": False,
                "message": "Unsupported document type or missing content",
                "document_count": 0
            }
        
        if not documents:
            return {
                "success": False,
                "message": "Failed to process document into chunks",
                "document_count": 0
            }
        
        # Add to pipeline
        pipeline = get_rag_pipeline()
        success = pipeline.add_documents(documents)
        
        return {
            "success": success,
            "message": f"Added {len(documents)} document chunks to RAG system" if success else "Failed to add document",
            "document_count": len(documents) if success else 0
        }
    
    except Exception as e:
        logger.error(f"Error adding document to RAG system: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "document_count": 0
        }

def get_rag_system_status() -> Dict[str, Any]:
    """Get the status of the RAG system"""
    try:
        chroma_store = get_chroma_store()
        stats = chroma_store.get_collection_stats()
        
        return {
            "status": "active",
            "vector_store": {
                "type": "chroma",
                "collection": stats.get("collection_name"),
                "document_count": stats.get("document_count", 0)
            },
            "embeddings": {
                "type": "simple" if "OpenAIEmbeddings" not in str(type(chroma_store.embeddings)) else "openai"
            },
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting RAG system status: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }

def reset_rag_system() -> Dict[str, Any]:
    """Reset the entire RAG system"""
    try:
        reset_rag_pipeline()
        return {
            "success": True,
            "message": "RAG system reset successfully",
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error resetting RAG system: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }