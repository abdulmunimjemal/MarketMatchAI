#!/usr/bin/env python3
"""
Management script for the vector store.
This script can be used to switch between FAISS and Pinecone.
"""

import os
import sys
import json
import logging
from utils.config import (
    set_vector_store_type, 
    get_vector_store_type, 
    is_pinecone_available, 
    is_openai_available,
    get_system_status
)

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
    print("  check-openai - Check if OpenAI is available")
    print("  check-all - Check status of all components")

def show_status():
    """Show current vector store status"""
    status = get_system_status()
    
    print("=== System Status ===")
    print(f"Current vector store type: {status['vector_store_type']}")
    print(f"Pinecone available: {'Yes' if status['pinecone_available'] else 'No'}")
    print(f"OpenAI available: {'Yes' if status['openai_available'] else 'No'}")
    
    if status['vector_store_type'] == 'pinecone' and not status['pinecone_available']:
        print("WARNING: Pinecone is selected but not available. Will fall back to FAISS.")

def switch_to_faiss():
    """Switch to FAISS vector store"""
    if set_vector_store_type('faiss'):
        print("Successfully switched to FAISS vector store")
        # Reset the vector store to force reinitialization
        from utils.vector_store_reset import reset_vector_store
        reset_vector_store()
    else:
        print("Failed to switch to FAISS vector store")

def switch_to_pinecone():
    """Switch to Pinecone vector store"""
    if not is_pinecone_available():
        print("ERROR: Pinecone is not available. Please set PINECONE_API_KEY and PINECONE_ENVIRONMENT")
        return
    
    if set_vector_store_type('pinecone'):
        print("Successfully switched to Pinecone vector store")
        # Reset the vector store to force reinitialization
        from utils.vector_store_reset import reset_vector_store
        reset_vector_store()
    else:
        print("Failed to switch to Pinecone vector store")

def check_pinecone():
    """Check if Pinecone is available"""
    if is_pinecone_available():
        print("Pinecone is available and configured correctly")
        # Try to import pinecone
        try:
            import pinecone
            print("Pinecone package is installed")
            # Get Pinecone credentials from environment
            api_key = os.environ.get("PINECONE_API_KEY")
            environment = os.environ.get("PINECONE_ENVIRONMENT")
            print(f"Environment: {environment}")
            # Test connection (don't print API key for security)
            try:
                pc = pinecone.Pinecone(api_key=api_key)
                indexes = [index.name for index in pc.list_indexes()]
                print(f"Connected to Pinecone successfully. Available indexes: {indexes}")
            except Exception as e:
                print(f"Error connecting to Pinecone: {str(e)}")
        except ImportError:
            print("Pinecone package is not installed")
    else:
        print("Pinecone is not available")
        print("Please set the following environment variables:")
        print("  - PINECONE_API_KEY")
        print("  - PINECONE_ENVIRONMENT")

def check_openai():
    """Check if OpenAI is available"""
    if is_openai_available():
        print("OpenAI API key is available and configured correctly")
        # Try to import openai
        try:
            import openai
            print("OpenAI package is installed")
            # Test connection (don't use actual API calls to avoid charges)
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key and api_key[:3] == "sk-":
                print("OpenAI API key has the correct format")
            else:
                print("WARNING: OpenAI API key doesn't have the expected format (should start with 'sk-')")
        except ImportError:
            print("OpenAI package is not installed")
    else:
        print("OpenAI API key is not available")
        print("Please set the following environment variable:")
        print("  - OPENAI_API_KEY")

def check_all():
    """Check status of all components"""
    status = get_system_status()
    
    print("=== Complete System Status ===")
    print(json.dumps(status, indent=2))
    
    # Check components in detail
    print("\n=== Checking Pinecone ===")
    check_pinecone()
    
    print("\n=== Checking OpenAI ===")
    check_openai()
    
    print("\n=== Vector Store Configuration ===")
    print(f"Current vector store type: {status['vector_store_type']}")
    if status['vector_store_type'] == 'pinecone':
        if status['pinecone_available']:
            print("✓ Pinecone is configured and available")
        else:
            print("✗ Pinecone is selected but not available")
    else:
        print("✓ Using local FAISS vector store")

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
    elif command == "check-openai":
        check_openai()
    elif command == "check-all":
        check_all()
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)