"""
Document processors package for the RAG system.
"""

from app.rag.document_processors.text_splitter import split_text
from app.rag.document_processors.processor import (
    process_file, 
    process_text_file, 
    process_pdf_file,
    process_doc_file,
    process_text
)

__all__ = [
    'split_text', 
    'process_file', 
    'process_text_file', 
    'process_pdf_file',
    'process_doc_file',
    'process_text'
]