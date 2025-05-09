#!/usr/bin/env python3
"""
Test script for Pinecone integration.
This script tests the Pinecone vector store by adding and retrieving documents.
"""

import logging
from app import app
from utils.config import set_vector_store_type, is_pinecone_available
from utils.embedding import get_embeddings
from utils.vector_store import reset_vector_store, get_vector_store, add_text_to_vector_store

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pinecone():
    """Test Pinecone integration"""
    print("Testing Pinecone integration...")
    
    # Check if Pinecone is available
    if not is_pinecone_available():
        print("Pinecone is not available. Please set PINECONE_API_KEY and PINECONE_ENVIRONMENT.")
        print("Falling back to FAISS for testing...")
        set_vector_store_type('faiss')
    else:
        # Preserve current vector store type
        from utils.config import get_vector_store_type
        current_store = get_vector_store_type()
        print(f"Using current vector store type: {current_store}")
    
    # Reset vector store to force reinitialization
    print("Resetting vector store...")
    reset_vector_store()
    
    # Get vector store
    print("Getting vector store...")
    with app.app_context():
        vector_store = get_vector_store()
        
        # Create some test data
        test_documents = [
            "The market for renewable energy is growing rapidly, with solar power leading the way.",
            "Artificial intelligence is transforming how businesses analyze customer data.",
            "E-commerce platforms are expanding into new markets across Southeast Asia.",
            "Healthcare technology innovations are reducing costs and improving patient outcomes.",
            "Financial technology startups are disrupting traditional banking services."
        ]
        
        # Add documents to vector store
        print("Adding documents to vector store...")
        for i, text in enumerate(test_documents):
            metadata = {
                "document_id": f"test-{i}",
                "title": f"Test Document {i}",
                "chunk_id": f"chunk-{i}",
                "chunk_index": i
            }
            add_text_to_vector_store(text, metadata)
        
        # Wait a moment for documents to be indexed
        import time
        print("Waiting for documents to be indexed...")
        time.sleep(2)
        
        # Test queries
        test_queries = [
            "renewable energy market trends",
            "AI in business analytics",
            "e-commerce expansion strategies",
            "healthcare technology innovations",
            "fintech disrupting banking"
        ]
        
        # Search for documents
        print("\nTesting queries...")
        for query in test_queries:
            print(f"\nQuery: {query}")
            results = vector_store.similarity_search_with_score(query, k=2)
            
            if results:
                print(f"Found {len(results)} results:")
                for doc, score in results:
                    print(f"- {doc.page_content} (Score: {score:.4f})")
            else:
                print("No results found.")
    
    print("\nTest completed successfully!")
    return True

if __name__ == "__main__":
    test_pinecone()