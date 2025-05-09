"""
Text splitter for the RAG system.

This module provides functionality to split documents into chunks for processing.
"""

import logging
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document as LangchainDocument

from app.rag.config.constants import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

def split_text(text: str, metadata: Optional[Dict[str, Any]] = None) -> List[LangchainDocument]:
    """Split text into chunks suitable for embedding and storage"""
    if not text:
        logger.warning("Empty text provided to split_text")
        return []
    
    try:
        # Create a text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # If metadata is provided, create a Document first
        if metadata:
            doc = LangchainDocument(page_content=text, metadata=metadata)
            chunks = text_splitter.split_documents([doc])
        else:
            # Split the raw text and then convert to Documents
            chunk_texts = text_splitter.split_text(text)
            chunks = [
                LangchainDocument(
                    page_content=chunk,
                    metadata=metadata or {"chunk_index": i}
                )
                for i, chunk in enumerate(chunk_texts)
            ]
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    except Exception as e:
        logger.error(f"Error splitting text: {str(e)}")
        # Return a single chunk as fallback
        return [LangchainDocument(
            page_content=text[:CHUNK_SIZE] if len(text) > CHUNK_SIZE else text,
            metadata=metadata or {"chunk_index": 0, "error": "Failed to split properly"}
        )]