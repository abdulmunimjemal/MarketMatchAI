"""
Document processor for the RAG system.

This module provides functionality to process documents for ingestion into the vector store.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from langchain.docstore.document import Document as LangchainDocument
from app.rag.config.constants import MAX_DOCUMENT_SIZE_MB
from app.rag.document_processors.text_splitter import split_text

logger = logging.getLogger(__name__)

def process_file(
    file_path: str, 
    metadata: Optional[Dict[str, Any]] = None
) -> List[LangchainDocument]:
    """Process a file and return LangChain Document chunks"""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return []
    
    # Check file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > MAX_DOCUMENT_SIZE_MB:
        logger.error(f"File too large: {file_path} ({file_size_mb:.2f} MB > {MAX_DOCUMENT_SIZE_MB} MB)")
        return []
    
    try:
        # Determine file type from extension
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()
        
        # Process based on file type
        if extension in ['.txt', '.md', '.csv']:
            return process_text_file(file_path, metadata)
        elif extension in ['.pdf']:
            return process_pdf_file(file_path, metadata)
        elif extension in ['.docx', '.doc']:
            return process_doc_file(file_path, metadata)
        else:
            logger.warning(f"Unsupported file type: {extension}")
            return []
    
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        return []

def process_text_file(
    file_path: str,
    metadata: Optional[Dict[str, Any]] = None
) -> List[LangchainDocument]:
    """Process a text file and return document chunks"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Create base metadata
        base_metadata = metadata or {}
        base_metadata.update({
            "source": file_path,
            "file_type": "text"
        })
        
        # Split the text into chunks
        return split_text(text, base_metadata)
    
    except Exception as e:
        logger.error(f"Error processing text file {file_path}: {str(e)}")
        return []

def process_pdf_file(
    file_path: str,
    metadata: Optional[Dict[str, Any]] = None
) -> List[LangchainDocument]:
    """Process a PDF file and return document chunks"""
    try:
        from langchain.document_loaders import PyPDFLoader
        
        # Load the PDF file
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Add metadata to each document
        for doc in documents:
            doc.metadata.update(metadata or {})
            doc.metadata["source"] = file_path
            doc.metadata["file_type"] = "pdf"
        
        logger.info(f"Processed PDF {file_path} into {len(documents)} pages")
        
        # Further split each page if necessary
        result = []
        for doc in documents:
            chunks = split_text(doc.page_content, doc.metadata)
            result.extend(chunks)
        
        return result
    
    except ImportError:
        logger.error("PyPDF loader not available")
        return []
    except Exception as e:
        logger.error(f"Error processing PDF file {file_path}: {str(e)}")
        return []

def process_doc_file(
    file_path: str,
    metadata: Optional[Dict[str, Any]] = None
) -> List[LangchainDocument]:
    """Process a Word document and return document chunks"""
    try:
        from langchain.document_loaders import Docx2txtLoader
        
        # Load the Word document
        loader = Docx2txtLoader(file_path)
        documents = loader.load()
        
        # Add metadata to each document
        for doc in documents:
            doc.metadata.update(metadata or {})
            doc.metadata["source"] = file_path
            doc.metadata["file_type"] = "docx"
        
        logger.info(f"Processed Word document {file_path}")
        
        # Further split the document
        result = []
        for doc in documents:
            chunks = split_text(doc.page_content, doc.metadata)
            result.extend(chunks)
        
        return result
    
    except ImportError:
        logger.error("Docx2txt loader not available")
        return []
    except Exception as e:
        logger.error(f"Error processing Word file {file_path}: {str(e)}")
        return []

def process_text(
    text: str,
    metadata: Optional[Dict[str, Any]] = None
) -> List[LangchainDocument]:
    """Process raw text and return document chunks"""
    if not text:
        logger.warning("Empty text provided")
        return []
    
    try:
        # Create base metadata
        base_metadata = metadata or {}
        base_metadata.update({
            "source": "direct_text",
            "file_type": "text"
        })
        
        # Split the text into chunks
        return split_text(text, base_metadata)
    
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        return []