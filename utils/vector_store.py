import os
import uuid
import logging
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain.docstore.document import Document as LangchainDocument
import pinecone

from app import db
from models import Document, DocumentChunk
from utils.embedding import get_embeddings

logger = logging.getLogger(__name__)

# Singleton pattern for vector store
_vector_store = None
_pinecone_index_name = "marketmatch"  # Index name must be lowercase with no special chars

def reset_vector_store():
    """Reset the vector store singleton to force reinitialization"""
    global _vector_store
    _vector_store = None
    logger.info("Vector store reset, will be reinitialized on next access")

def get_vector_store_type():
    """Get the configured vector store type"""
    return os.environ.get("VECTOR_STORE_TYPE", "faiss").lower()

def initialize_pinecone():
    """Initialize the Pinecone client"""
    try:
        # Get Pinecone credentials from environment variables
        pinecone_api_key = os.environ.get("PINECONE_API_KEY")
        pinecone_environment = os.environ.get("PINECONE_ENVIRONMENT")
        
        if not pinecone_api_key or not pinecone_environment:
            logger.warning("Pinecone credentials not found. Falling back to FAISS.")
            return False
        
        # Initialize Pinecone with new API
        pc = pinecone.Pinecone(api_key=pinecone_api_key)
        
        try:
            # Check if index exists
            index_list = [index.name for index in pc.list_indexes()]
            
            if _pinecone_index_name not in index_list:
                logger.info(f"Pinecone index '{_pinecone_index_name}' doesn't exist yet")
                # For now, we'll use FAISS instead of creating a new index
                # This is because index creation can take time and might fail
                return False
            else:
                logger.info(f"Using existing Pinecone index: {_pinecone_index_name}")
                return True
        except Exception as e:
            logger.error(f"Error checking Pinecone indexes: {str(e)}")
            return False
        
    except Exception as e:
        logger.error(f"Error initializing Pinecone: {str(e)}")
        return False

def get_vector_store():
    """Get or create a vector store instance (Pinecone or FAISS fallback)"""
    global _vector_store
    
    if _vector_store is not None:
        return _vector_store
    
    # Get the store type from environment
    vector_store_type = get_vector_store_type()
    logger.info(f"Initializing vector store, type={vector_store_type}")
    
    try:
        # Get the embedding model
        embeddings = get_embeddings()
        
        # Get all document chunks from the database
        chunks = DocumentChunk.query.all()
        
        # Create LangChain documents from the database chunks
        documents = []
        for chunk in chunks:
            document = Document.query.get(chunk.document_id)
            if document and chunk.content:
                doc = LangchainDocument(
                    page_content=chunk.content,
                    metadata={
                        "chunk_id": str(chunk.id),  # Convert to string for Pinecone
                        "document_id": str(chunk.document_id),
                        "document_title": document.title,
                        "chunk_index": chunk.chunk_index
                    }
                )
                documents.append(doc)
        
        logger.info(f"Found {len(documents)} document chunks in database")
        
        # Try to use Pinecone if credentials are available and it's enabled
        if vector_store_type == "pinecone" and initialize_pinecone():
            try:
                # Get Pinecone credentials for LangChain integration
                pinecone_api_key = os.environ.get("PINECONE_API_KEY")
                
                if not documents:
                    # Create an empty Pinecone vector store
                    placeholder_doc = LangchainDocument(
                        page_content="This is a placeholder document to initialize the vector store.",
                        metadata={"chunk_id": "placeholder", "document_id": "placeholder"}
                    )
                    
                    _vector_store = LangchainPinecone.from_documents(
                        documents=[placeholder_doc],
                        embedding=embeddings,
                        index_name=_pinecone_index_name,
                        pinecone_api_key=pinecone_api_key
                    )
                else:
                    # Create a Pinecone vector store with existing documents
                    _vector_store = LangchainPinecone.from_documents(
                        documents=documents,
                        embedding=embeddings,
                        index_name=_pinecone_index_name,
                        pinecone_api_key=pinecone_api_key
                    )
                
                logger.info("Successfully initialized Pinecone vector store")
                return _vector_store
            except Exception as e:
                logger.error(f"Error creating Pinecone vector store: {str(e)}")
                # Fall back to FAISS
                logger.info("Falling back to FAISS vector store")
        
        # Use FAISS if Pinecone is not available or fails
        logger.info("Initializing FAISS vector store")
        
        if not documents:
            # Create an empty FAISS vector store
            _vector_store = FAISS.from_texts(
                texts=["This is a placeholder document to initialize the vector store."], 
                embedding=embeddings,
                metadatas=[{"chunk_id": "placeholder", "document_id": "placeholder"}]
            )
        else:
            # Create a FAISS vector store with existing documents
            _vector_store = FAISS.from_documents(documents=documents, embedding=embeddings)
        
        logger.info("Successfully initialized FAISS vector store")
        return _vector_store
    
    except Exception as e:
        logger.error(f"Error initializing vector store: {str(e)}")
        raise

def add_text_to_vector_store(text, metadata):
    """Add a single text to the vector store"""
    vector_store = get_vector_store()
    
    try:
        # Add text to vector store
        vector_store.add_texts(texts=[text], metadatas=[metadata])
        logger.info(f"Added text to vector store with metadata: {metadata}")
        return vector_store
    except Exception as e:
        logger.error(f"Error adding text to vector store: {str(e)}")
        raise

def add_documents_to_vector_store(texts, metadatas):
    """Add multiple documents to the vector store"""
    vector_store = get_vector_store()
    
    try:
        # Add texts to vector store
        vector_store.add_texts(texts=texts, metadatas=metadatas)
        logger.info(f"Added {len(texts)} documents to vector store")
        return vector_store
    except Exception as e:
        logger.error(f"Error adding documents to vector store: {str(e)}")
        raise

def search_vector_store(query, k=5):
    """Search the vector store for relevant documents"""
    vector_store = get_vector_store()
    
    try:
        logger.info(f"Searching vector store for: '{query}'")
        results = vector_store.similarity_search_with_score(query, k=k)
        logger.info(f"Found {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Error searching vector store: {str(e)}")
        # Return empty results in case of error
        return []
