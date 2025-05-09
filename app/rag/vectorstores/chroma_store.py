"""
ChromaDB vector store implementation for the RAG system.

This module provides ChromaDB vector store functionality.
"""

import logging
import chromadb
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document as LangchainDocument
from typing import List, Dict, Any, Tuple, Optional

from app.rag.config.constants import CHROMA_PERSIST_DIRECTORY
from app.rag.embeddings import get_embeddings

logger = logging.getLogger(__name__)

class ChromaStore:
    """ChromaDB vector store for the AI Market Matching Tool"""
    
    def __init__(self, collection_name: str = "market_matching"):
        """Initialize the ChromaDB vector store"""
        self.collection_name = collection_name
        self.embeddings = get_embeddings()
        self.persist_directory = CHROMA_PERSIST_DIRECTORY
        self._vector_store = None
        logger.info(f"Initialized ChromaStore with collection: {collection_name}")
    
    def _get_or_create_store(self):
        """Get or create the ChromaDB vector store"""
        if self._vector_store is None:
            try:
                # Try to load existing store
                self._vector_store = Chroma(
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=self.persist_directory
                )
                logger.info(f"Loaded existing ChromaDB collection: {self.collection_name}")
            except Exception as e:
                logger.warning(f"Error loading ChromaDB: {str(e)}, creating new collection")
                # Create a new empty store
                self._vector_store = Chroma.from_documents(
                    documents=[
                        LangchainDocument(
                            page_content="This is a placeholder document to initialize the vector store.",
                            metadata={"source": "placeholder"}
                        )
                    ],
                    embedding=self.embeddings,
                    collection_name=self.collection_name,
                    persist_directory=self.persist_directory
                )
                logger.info(f"Created new ChromaDB collection: {self.collection_name}")
        
        return self._vector_store
    
    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> List[str]:
        """Add texts to the vector store"""
        store = self._get_or_create_store()
        try:
            ids = store.add_texts(texts=texts, metadatas=metadatas)
            store.persist()
            logger.info(f"Added {len(texts)} texts to ChromaDB")
            return ids
        except Exception as e:
            logger.error(f"Error adding texts to ChromaDB: {str(e)}")
            raise
    
    def add_documents(self, documents: List[LangchainDocument]) -> List[str]:
        """Add LangChain documents to the vector store"""
        store = self._get_or_create_store()
        try:
            ids = store.add_documents(documents=documents)
            store.persist()
            logger.info(f"Added {len(documents)} documents to ChromaDB")
            return ids
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {str(e)}")
            raise
    
    def similarity_search_with_score(
        self, query: str, k: int = 5
    ) -> List[Tuple[LangchainDocument, float]]:
        """Search for similar documents"""
        store = self._get_or_create_store()
        try:
            results = store.similarity_search_with_score(query, k=k)
            logger.info(f"Found {len(results)} results for query: '{query}'")
            return results
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {str(e)}")
            return []
    
    def delete_collection(self) -> bool:
        """Delete the entire collection"""
        try:
            client = chromadb.PersistentClient(path=self.persist_directory)
            client.delete_collection(name=self.collection_name)
            self._vector_store = None
            logger.info(f"Deleted ChromaDB collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting ChromaDB collection: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            client = chromadb.PersistentClient(path=self.persist_directory)
            collection = client.get_collection(name=self.collection_name)
            count = collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Error getting ChromaDB stats: {str(e)}")
            return {
                "collection_name": self.collection_name,
                "document_count": 0,
                "status": "error",
                "error": str(e)
            }

# Singleton pattern
_chroma_store_instance = None

def get_chroma_store() -> ChromaStore:
    """Get the shared ChromaDB store instance"""
    global _chroma_store_instance
    if _chroma_store_instance is None:
        _chroma_store_instance = ChromaStore()
    return _chroma_store_instance

def reset_chroma_store() -> None:
    """Reset the ChromaDB store singleton"""
    global _chroma_store_instance
    _chroma_store_instance = None
    logger.info("ChromaDB store reset, will be reinitialized on next access")