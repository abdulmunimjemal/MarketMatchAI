# AI Market Matching Tool

A Flask-based tool that uses RAG (Retrieval-Augmented Generation) to match market opportunities by analyzing uploaded documents.

## Features

- Document uploading and processing
- RAG pipeline for advanced market matching
- Dual vector store strategy (Pinecone & FAISS)
- Automated document chunking and embedding
- Simple web interface

## Technical Architecture

This application uses a modern RAG architecture:

1. **Document Ingestion**: Upload documents through the web interface
2. **Document Processing**: Automatic chunking and embedding generation
3. **Vector Storage**: Dual storage strategy (cloud with Pinecone, local with FAISS)
4. **Query Processing**: Semantic search and answer generation with LLM

## Vector Store Strategy

The application implements a dual vector store strategy:

- **Pinecone**: Cloud-based vector database for production use
  - Scalable for large document collections
  - Persistent across application restarts
  - Requires API keys

- **FAISS**: Local vector database as fallback
  - Works without external dependencies
  - In-memory storage (non-persistent)
  - Good for development and testing

You can switch between vector stores using the management script:

```
python manage_vector_store.py status      # Check current status
python manage_vector_store.py use-faiss   # Switch to FAISS
python manage_vector_store.py use-pinecone # Switch to Pinecone
```

## Environment Variables

The application uses the following environment variables:

- `OPENAI_API_KEY`: OpenAI API key for embeddings and completion
- `PINECONE_API_KEY`: Pinecone API key for cloud vector storage
- `PINECONE_ENVIRONMENT`: Pinecone environment (e.g., "us-east-1")
- `VECTOR_STORE_TYPE`: Set to "pinecone" or "faiss" (default: "faiss")

## Development

Requirements:
- Python 3.11+
- Flask for web interface
- LangChain for RAG pipeline
- FAISS for local vector storage
- Pinecone for cloud vector storage
- OpenAI for embeddings and completion

To run the development server:

```
python main.py
```

## Testing

To test the vector store functionality:

```
python test_pinecone.py
```