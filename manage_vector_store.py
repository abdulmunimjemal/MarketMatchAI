#!/usr/bin/env python3
"""
Management script for the vector store.
This script can be used to switch between FAISS and Pinecone.
"""

import os
import sys
import logging
from utils.vector_store_config import set_vector_store_type, get_vector_store_type, is_pinecone_available

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_usage():
    """Print usage information"""
    print("Usage: python manage_vector_store.py [command]")
    print("Commands:")
    print("  status - Show current vector store status")
    print("  use-faiss - Switch to FAISS vector store")
    print("  use-pinecone - Switch to Pinecone vector store")
    print("  check-pinecone - Check if Pinecone is available")

def show_status():
    """Show current vector store status"""
    current_type = get_vector_store_type()
    pinecone_available = is_pinecone_available()
    
    print(f"Current vector store type: {current_type}")
    print(f"Pinecone available: {'Yes' if pinecone_available else 'No'}")
    
    if current_type == 'pinecone' and not pinecone_available:
        print("WARNING: Pinecone is selected but not available. Will fall back to FAISS.")

def switch_to_faiss():
    """Switch to FAISS vector store"""
    if set_vector_store_type('faiss'):
        print("Successfully switched to FAISS vector store")
    else:
        print("Failed to switch to FAISS vector store")

def switch_to_pinecone():
    """Switch to Pinecone vector store"""
    if not is_pinecone_available():
        print("ERROR: Pinecone is not available. Please set PINECONE_API_KEY and PINECONE_ENVIRONMENT")
        return
    
    if set_vector_store_type('pinecone'):
        print("Successfully switched to Pinecone vector store")
    else:
        print("Failed to switch to Pinecone vector store")

def check_pinecone():
    """Check if Pinecone is available"""
    if is_pinecone_available():
        print("Pinecone is available and configured correctly")
    else:
        print("Pinecone is not available")
        print("Please set the following environment variables:")
        print("  - PINECONE_API_KEY")
        print("  - PINECONE_ENVIRONMENT")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        show_status()
    elif command == "use-faiss":
        switch_to_faiss()
    elif command == "use-pinecone":
        switch_to_pinecone()
    elif command == "check-pinecone":
        check_pinecone()
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)