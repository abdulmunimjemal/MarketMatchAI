import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
import uuid

from app import db
from models import Document, DocumentChunk
from utils.embedding import embed_text
from utils.vector_store import add_text_to_vector_store

logger = logging.getLogger(__name__)

def process_document(document_id):
    """Process a document: split into chunks, generate embeddings, and store in vector database"""
    try:
        # Get the document from the database
        document = Document.query.get(document_id)
        if not document:
            logger.error(f"Document with ID {document_id} not found")
            return False
        
        # Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        chunks = text_splitter.split_text(document.content)
        
        # Create document chunks in the database and generate embeddings
        for i, chunk_text in enumerate(chunks):
            # Create document chunk
            chunk = DocumentChunk(
                content=chunk_text,
                chunk_index=i,
                document_id=document.id
            )
            db.session.add(chunk)
            db.session.commit()
            
            # Generate embedding for the chunk
            try:
                embedding = embed_text(chunk_text)
                
                # Store the embedding ID reference
                chunk.embedding_id = str(uuid.uuid4())
                db.session.commit()
                
                # Add to vector store
                metadata = {
                    "chunk_id": chunk.id,
                    "document_id": document.id,
                    "document_title": document.title,
                    "chunk_index": i
                }
                add_text_to_vector_store(chunk_text, metadata)
                
            except Exception as e:
                logger.error(f"Error generating embedding for chunk {chunk.id}: {str(e)}")
                continue
        
        # Mark the document as processed
        document.processed = True
        db.session.commit()
        
        logger.info(f"Document {document_id} processed successfully with {len(chunks)} chunks")
        return True
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        return False
