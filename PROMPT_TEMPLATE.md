# Comprehensive Prompt Template for AI Market Matching Tool with RAG

## Overview
This prompt template will guide an AI model (specifically Gemini or similar) to generate a complete MVP codebase for an AI Market Matching Tool with Retrieval Augmented Generation (RAG) capabilities, following the blueprint of a Flask backend with a JavaScript frontend.

---

## Project Specification

### Core Capabilities

I need you to create a full-stack application that leverages RAG technology to help match market needs with relevant information from documents. The application should:

1. Allow users to upload market data documents (e.g., research reports, industry analyses)
2. Process and embed these documents using vector embeddings
3. Enable natural language queries about market information
4. Return relevant, evidence-based answers with source attribution
5. Maintain a history of queries and responses for reference

### Technical Stack

- **Backend**:
  - Python 3.10+ as the core language
  - Flask for web framework and routing
  - SQLAlchemy for database ORM
  - LangChain for orchestrating the RAG pipeline
  - OpenAI/Gemini embeddings (with fallback to local models)
  - FAISS vector database for efficient similarity search
  - Document processing with text chunking capabilities

- **Frontend**:
  - Clean HTML5/CSS3 with responsive design
  - Vanilla JavaScript for interactivity (no frameworks required)
  - Bootstrap 5 for styling and components
  - Chart.js for data visualization
  - Axios for API calls

- **Database**:
  - SQLite for development (with option to switch to PostgreSQL)
  - Vector store for embeddings
  - Relational tables for user data, documents, and query history

### Application Structure

```
/
├── app.py                  # Flask application setup
├── main.py                 # Application entry point
├── models.py               # SQLAlchemy models
├── routes.py               # Flask routes
├── static/                 # Static assets
│   ├── css/                # CSS stylesheets
│   ├── js/                 # JavaScript files
│   └── img/                # Images and icons
├── templates/              # HTML templates
│   ├── layout.html         # Base template
│   ├── index.html          # Landing page
│   ├── documents.html      # Document management
│   └── query.html          # Query interface
├── utils/                  # Utility modules
│   ├── document_processor.py  # Document handling
│   ├── embedding.py        # Vector embedding
│   ├── rag_pipeline.py     # RAG implementation
│   └── vector_store.py     # FAISS integration
└── uploads/                # Document upload directory
```

### Key Features

1. **Document Management**:
   - Upload interface with drag-and-drop support
   - Document processing status tracking
   - Document preview and metadata display
   - Automatic chunking of documents into optimal segments

2. **Query Interface**:
   - Natural language query input
   - Response display with confidence scores
   - Source attribution with links to original documents
   - Query history and saved queries

3. **RAG Implementation**:
   - Embedding generation for documents and queries
   - Similarity search for relevant context retrieval
   - LLM integration for generating coherent responses
   - Source ranking and relevance scoring

4. **Analytics Dashboard**:
   - Document statistics
   - Query patterns and frequency
   - System performance metrics
   - Visualization of document relationships

### Visual Design

The interface should follow these design principles:

- Color Scheme:
  - Primary: #4285F4 (Google Blue)
  - Secondary: #34A853 (Google Green)
  - Text: #202124 (Google Grey)
  - Background: #FFFFFF (White)
  - Code Block: #F8F9FA (Light Grey)

- Typography:
  - Headers: Google Sans, 500 weight
  - Body: Google Sans, 400 weight
  - Code: Roboto Mono, 400 weight

- Component Style:
  - Clean, modern interface with appropriate white space
  - Card-based content organization
  - Subtle shadows and rounded corners
  - Interactive elements with hover states
  - Responsive design for all screen sizes

---

## Development Process

1. **Setup and Configuration**:
   - Initialize Flask application with proper structure
   - Set up database models and relationships
   - Configure static and template directories
   - Implement basic routing

2. **Core Functionality**:
   - Implement document upload and processing
   - Create embedding generation pipeline
   - Set up vector store integration
   - Develop query processing system

3. **User Interface**:
   - Design responsive layouts
   - Implement interactive components
   - Create data visualization elements
   - Ensure accessible and intuitive experience

4. **Integration**:
   - Connect frontend to backend APIs
   - Integrate RAG pipeline with UI
   - Implement error handling and edge cases
   - Optimize for performance

5. **Testing and Refinement**:
   - Validate all user flows
   - Test with various document types
   - Optimize response times
   - Refine UI/UX based on usability

---

## Implementation Details

### RAG Pipeline Specifics

The RAG implementation should follow this pattern:

1. **Document Processing**:
   - Split documents into chunks of ~1000 tokens with 20% overlap
   - Generate embeddings for each chunk using embedding models
   - Store chunks and embeddings in vector database with metadata

2. **Query Processing**:
   - Generate embeddings for user queries
   - Retrieve top k (~5) most similar document chunks
   - Construct prompt with retrieved context and user query
   - Generate response with appropriate attribution

3. **Response Handling**:
   - Format response with sources clearly indicated
   - Calculate and display relevance scores
   - Save query and response for future reference
   - Allow refinement of queries based on results

### Security Considerations

- Implement proper input validation
- Sanitize document uploads
- Use environment variables for sensitive values
- Implement basic authentication when necessary

### Performance Optimization

- Implement caching for frequent queries
- Optimize vector search parameters
- Use background tasks for document processing
- Implement pagination for large result sets

---

## Output Requirements

The complete codebase should:

1. Be fully functional with clear documentation
2. Follow best practices for each technology used
3. Include error handling and edge cases
4. Be optimized for both development and production
5. Be organized in a clear, maintainable structure
6. Include responsive and intuitive user interfaces
7. Implement all core RAG capabilities efficiently

---

## Additional Guidance

- Prioritize code quality over quantity
- Include helpful comments explaining key design decisions
- Design the UI to be intuitive for non-technical users
- Ensure the application is extensible for future features
- Provide fallbacks for cases where external services are unavailable
- Optimize for developer experience with clear patterns

---

I'm looking for a detailed, production-ready implementation following this blueprint closely. The final code should be complete, functional, and well-structured.