"""
RAG pipeline for the AI Market Matching Tool.

This module provides the main Retrieval Augmented Generation pipeline.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from langchain.docstore.document import Document as LangchainDocument
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.llms.fake import FakeListLLM

from app.rag.vectorstores import get_chroma_store
from app.rag.embeddings import get_embeddings

logger = logging.getLogger(__name__)

# Default prompt template for the RAG pipeline
DEFAULT_PROMPT_TEMPLATE = """
You are an AI market matching assistant that helps users find relevant market information.

CONTEXT:
{context}

QUESTION:
{question}

Your task is to answer the question based on the context provided. 
If the answer is not contained within the context, say "I don't have enough information to answer this question." 
and suggest a better question to ask.

ANSWER:
"""

class RAGPipeline:
    """Main RAG Pipeline for the AI Market Matching Tool"""
    
    def __init__(self, prompt_template: Optional[str] = None):
        """Initialize the RAG pipeline"""
        self.prompt_template = prompt_template or DEFAULT_PROMPT_TEMPLATE
        self.chroma_store = get_chroma_store()
        self.embeddings = get_embeddings()
        self._pipeline = None
        logger.info("Initialized RAG pipeline")
    
    def _initialize_llm(self):
        """Initialize a language model for the pipeline"""
        try:
            # Try to use OpenAI if key is available
            import os
            openai_key = os.environ.get("OPENAI_API_KEY")
            
            if openai_key:
                from langchain.llms import OpenAI
                logger.info("Using OpenAI as LLM for the RAG pipeline")
                return OpenAI(temperature=0.7)
        except ImportError:
            logger.warning("OpenAI package not available")
        except Exception as e:
            logger.warning(f"Error initializing OpenAI LLM: {str(e)}")
        
        # Fall back to a fake LLM for testing
        logger.warning("Using fake LLM for testing (no real generation capability)")
        return FakeListLLM(
            responses=[
                "I've analyzed the market data and found relevant matches.",
                "Based on the information provided, here are the market opportunities.",
                "The market trends suggest several potential matches for your criteria.",
                "I don't have enough information to answer this question."
            ]
        )
    
    def _get_or_create_pipeline(self):
        """Get or create the RAG pipeline"""
        if self._pipeline is None:
            try:
                # Create prompt
                prompt = PromptTemplate(
                    template=self.prompt_template,
                    input_variables=["context", "question"]
                )
                
                # Get the vector store
                vector_store = self.chroma_store._get_or_create_store()
                
                # Initialize LLM
                llm = self._initialize_llm()
                
                # Create the chain
                self._pipeline = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
                    chain_type_kwargs={"prompt": prompt}
                )
                
                logger.info("Created RAG pipeline")
            
            except Exception as e:
                logger.error(f"Error creating RAG pipeline: {str(e)}")
                raise
        
        return self._pipeline
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a query through the RAG pipeline
        
        Returns a dictionary with:
        - answer: The generated answer
        - sources: List of source documents used
        - metadata: Additional information about the query
        """
        try:
            logger.info(f"Processing query: '{question}'")
            
            # Get the pipeline
            pipeline = self._get_or_create_pipeline()
            
            # First get the relevant documents for sources
            vector_store = self.chroma_store._get_or_create_store()
            docs_and_scores = vector_store.similarity_search_with_score(question, k=5)
            
            # Run the pipeline
            result = pipeline({"query": question})
            
            # Format the response
            response = {
                "query": question,
                "answer": result.get("result", "No answer generated"),
                "sources": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "relevance_score": score
                    }
                    for doc, score in docs_and_scores
                ],
                "metadata": {
                    "document_count": len(docs_and_scores),
                    "timestamp": __import__("datetime").datetime.now().isoformat()
                }
            }
            
            logger.info(f"Generated answer with {len(docs_and_scores)} sources")
            return response
        
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {str(e)}")
            return {
                "query": question,
                "answer": "I encountered an error while processing your query.",
                "sources": [],
                "metadata": {
                    "error": str(e),
                    "timestamp": __import__("datetime").datetime.now().isoformat()
                }
            }
    
    def add_document(self, document: LangchainDocument) -> bool:
        """Add a document to the RAG pipeline's vector store"""
        try:
            self.chroma_store.add_documents([document])
            logger.info(f"Added document to RAG pipeline: {document.metadata.get('source', 'unknown')}")
            # Reset the pipeline to use updated retriever
            self._pipeline = None
            return True
        except Exception as e:
            logger.error(f"Error adding document to RAG pipeline: {str(e)}")
            return False
    
    def add_documents(self, documents: List[LangchainDocument]) -> bool:
        """Add multiple documents to the RAG pipeline's vector store"""
        if not documents:
            logger.warning("Empty document list provided to add_documents")
            return False
        
        try:
            self.chroma_store.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to RAG pipeline")
            # Reset the pipeline to use updated retriever
            self._pipeline = None
            return True
        except Exception as e:
            logger.error(f"Error adding documents to RAG pipeline: {str(e)}")
            return False
    
    def reset(self) -> bool:
        """Reset the pipeline and its vector store"""
        try:
            self.chroma_store.delete_collection()
            self._pipeline = None
            logger.info("Reset RAG pipeline")
            return True
        except Exception as e:
            logger.error(f"Error resetting RAG pipeline: {str(e)}")
            return False

# Singleton pattern
_pipeline_instance = None

def get_rag_pipeline() -> RAGPipeline:
    """Get the shared RAG pipeline instance"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = RAGPipeline()
    return _pipeline_instance

def reset_rag_pipeline() -> None:
    """Reset the RAG pipeline singleton"""
    global _pipeline_instance
    if _pipeline_instance:
        _pipeline_instance.reset()
    _pipeline_instance = None
    logger.info("RAG pipeline reset, will be reinitialized on next access")