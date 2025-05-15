# Farmer Profiling System (Prototype Experiment 1)

An MVP implementation of a voice-first farmer profiling and hybrid search service, built with FastAPI and SQLAlchemy.

## Table of Contents

- [Overview](#overview)
- [Directory Structure](#directory-structure)
- [Requirements](#requirements)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the Service](#running-the-service)
- [API Endpoints](#api-endpoints)
- [Components & Modules](#components--modules)
- [Testing](#testing)
- [Docker Support](#docker-support)
- [Contributing](#contributing)

## Overview

This prototype provides:

- Voice-first farmer profiling: ingest farmer data through APIs, potentially via voice clients.
- Hybrid search: combine structured database lookup with vector-based semantic search.
- Modular architecture for ingestion, LLM processing, and vector storage.

## Directory Structure

```
prototype-experiment-1/
├── app/
│   ├── main.py               # FastAPI application entry point
│   ├── utils/database.py     # DB engine and session setup
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic schemas for request/response
│   ├── routes/
│   │   ├── farmers.py        # Farmer CRUD and profile endpoints
│   │   └── search.py         # Semantic and hybrid search endpoints
│   └── services/
│       ├── ingestion.py      # Data ingestion and preprocessing
│       ├── llm_processing.py # OpenAI/LLM-based profile insights
│       └── vector_db.py      # Vector store interface (e.g., FAISS)
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container build instructions
├── docker-compose.yml        # Compose setup with DB service
└── README.md                 # This documentation file
```

## Requirements

- Python 3.11+
- FastAPI
- Uvicorn (ASGI server)
- SQLAlchemy
- Pydantic
- (Optional) FAISS or another vector store

## Setup & Installation

1. Create and activate a Python virtual environment:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the database (default uses SQLite):
   ```bash
   export DATABASE_URL="sqlite:///./farmers.db"
   ```

## Configuration

Environment variables:

- `DATABASE_URL`: Database connection URL (e.g., `sqlite:///./farmers.db` or a Postgres URI)

## Running the Service

Start the FastAPI application:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit the interactive API docs at http://localhost:8000/docs

## API Endpoints

### Farmers

- `GET /api/v1/farmers/` : List all farmers
- `POST /api/v1/farmers/` : Create a new farmer profile
- `GET /api/v1/farmers/{id}` : Retrieve farmer by ID
- `PUT /api/v1/farmers/{id}` : Update farmer profile
- `DELETE /api/v1/farmers/{id}` : Remove a farmer

### Search

- `POST /api/v1/search/` : Submit a query payload for hybrid semantic search

Refer to the `/docs` endpoint for request/response schemas.

## Components & Modules

- **app/main.py**: Initializes the FastAPI app and routes.
- **app/utils/database.py**: Sets up SQLAlchemy engine and session.
- **app/models.py**: Defines ORM models for Farmer and related entities.
- **app/schemas.py**: Pydantic models for validation.
- **app/routes/**: Route definitions for farmers and search.
- **app/services/**:
  - **ingestion.py**: Handles raw data ingestion and preprocessing.
  - **llm_processing.py**: Interfaces with OpenAI or other LLMs for generating insights.
  - **vector_db.py**: Manages vector store operations for semantic search.

## Testing

Add tests using `pytest` or `unittest` in a `tests/` directory. Example:

```bash
pytest
```

## Docker Support

Build and run with Docker Compose:

```bash
docker-compose up --build
```

This sets up the API and a local database service (e.g., SQLite or PostgreSQL).

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/foo`
3. Commit your changes
4. Open a pull request

---
*Prototype Experiment 1: FastAPI-based MVP for Farmer Profiling*
