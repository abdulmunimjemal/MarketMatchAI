import os
import uuid
import logging
import numpy as np
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document as LangchainDocument

from app import db
from models import Document, DocumentChunk
from utils.embedding import get_embeddings

logger = logging.getLogger(__name__)

# Singleton pattern for vector store
_vector_store = None

def get_vector_store():
    """Get or create a FAISS vector store instance"""
    global _vector_store
    
    if _vector_store is not None:
        return _vector_store
    
    try:
        # Get all document chunks from the database
        chunks = DocumentChunk.query.all()
        
        # If there are no chunks yet, create an empty vector store
        if not chunks:
            embeddings = get_embeddings()
            _vector_store = FAISS.from_texts(
                ["This is a placeholder document to initialize the vector store."], 
                embeddings,
                metadatas=[{"chunk_id": "placeholder", "document_id": "placeholder"}]
            )
            return _vector_store
        
        # Get the embedding model
        embeddings = get_embeddings()
        
        # Create LangChain documents from the database chunks
        documents = []
        for chunk in chunks:
            document = Document.query.get(chunk.document_id)
            if document and chunk.content:
                doc = LangchainDocument(
                    page_content=chunk.content,
                    metadata={
                        "chunk_id": chunk.id,
                        "document_id": chunk.document_id,
                        "document_title": document.title,
                        "chunk_index": chunk.chunk_index
                    }
                )
                documents.append(doc)
        
        # Create or update the vector store
        if documents:
            _vector_store = FAISS.from_documents(documents, embeddings)
        else:
            _vector_store = FAISS.from_texts(
                ["This is a placeholder document to initialize the vector store."], 
                embeddings,
                metadatas=[{"chunk_id": "placeholder", "document_id": "placeholder"}]
            )
        
        return _vector_store
    
    except Exception as e:
        logger.error(f"Error initializing FAISS vector store: {str(e)}")
        raise

def add_text_to_vector_store(text, metadata):
    """Add a single text to the vector store"""
    vector_store = get_vector_store()
    embeddings = get_embeddings()
    
    vector_store.add_texts([text], [metadata], embeddings)
    return vector_store

def add_documents_to_vector_store(texts, metadatas):
    """Add multiple documents to the vector store"""
    vector_store = get_vector_store()
    embeddings = get_embeddings()
    
    vector_store.add_texts(texts, metadatas, embeddings)
    return vector_store

def search_vector_store(query, k=5):
    """Search the vector store for relevant documents"""
    vector_store = get_vector_store()
    results = vector_store.similarity_search_with_score(query, k=k)
    
    return results
