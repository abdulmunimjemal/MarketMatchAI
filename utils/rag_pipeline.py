import os
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate

from app import db
from models import Document, DocumentChunk, Query, Response
from utils.embedding import get_embeddings
from utils.vector_store import get_vector_store

logger = logging.getLogger(__name__)

def initialize_rag_pipeline():
    """Initialize the RAG pipeline with LangChain components"""
    try:
        # Get vector store client
        vector_store = get_vector_store()
        
        # Initialize the language model from OpenAI
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            logger.warning("OPENAI_API_KEY not found. RAG pipeline will not work properly.")
            # We'll continue but it will fail when actually trying to use the LLM
        
        llm = OpenAI(temperature=0.5, api_key=openai_api_key, model_name="gpt-3.5-turbo-instruct")
        
        # Create a prompt template for market matching
        prompt_template = """
        You are an AI assistant specialized in market matching, helping businesses find opportunities.
        Use the following context from the knowledge base to answer the question thoroughly.
        If the information isn't in the context, say "I don't have enough information in my knowledge base to answer this question."
        
        Context:
        {context}
        
        Question:
        {question}
        
        Please provide a detailed market-oriented answer with insights on:
        - Relevant market trends
        - Potential opportunities
        - Data-supported conclusions
        - Action recommendations where appropriate
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create the retrieval QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
            chain_type_kwargs={"prompt": prompt}
        )
        
        logger.info("RAG pipeline initialized successfully")
        return qa_chain
    
    except Exception as e:
        logger.error(f"Error initializing RAG pipeline: {str(e)}")
        raise

def query_rag_pipeline(query_text):
    """Process a query through the RAG pipeline and return the response with sources"""
    try:
        # Validate input
        if not query_text or not isinstance(query_text, str) or len(query_text.strip()) == 0:
            return "Please provide a valid query.", []
        
        # Get vector store
        vector_store = get_vector_store()
        
        # Search for relevant document chunks
        logger.info(f"Searching for documents relevant to: '{query_text}'")
        search_results = vector_store.similarity_search_with_score(query_text, k=5)
        
        # Extract document chunks and relevance scores
        source_chunks = []
        context_texts = []
        
        for doc, score in search_results:
            # Get chunk ID from metadata
            chunk_id = doc.metadata.get('chunk_id')
            if chunk_id and chunk_id != "placeholder":
                source_chunks.append((chunk_id, float(score)))
                context_texts.append(doc.page_content)
                logger.debug(f"Found relevant chunk: {chunk_id} with score {score}")
        
        # If no source chunks were found, return a default response
        if not source_chunks:
            logger.warning("No relevant documents found for query")
            return "I don't have enough information in my knowledge base to answer this question.", []
        
        # Create context from the retrieved chunks
        context = "\n\n---\n\n".join(context_texts)
        
        # Initialize the RAG chain
        try:
            qa_chain = initialize_rag_pipeline()
            
            # Check if we have an OpenAI API key before proceeding
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if not openai_api_key:
                # If no API key, return a formatted response with the context but no LLM processing
                formatted_response = "API key for OpenAI not found. Here are the most relevant documents from our knowledge base:\n\n"
                for i, text in enumerate(context_texts):
                    formatted_response += f"Document {i+1}:\n{text[:300]}...\n\n"
                return formatted_response, source_chunks
            
            # Run the query through the chain
            logger.info("Processing query through RAG pipeline")
            response = qa_chain({"query": query_text})
            
            return response['result'], source_chunks
            
        except Exception as e:
            logger.error(f"Error in RAG chain execution: {str(e)}")
            # Fallback to a simple response with contexts if the LLM fails
            formatted_response = "I encountered an issue processing your query with our AI model. Here are the most relevant documents I found:\n\n"
            for i, text in enumerate(context_texts):
                formatted_response += f"Document {i+1}:\n{text[:300]}...\n\n"
            return formatted_response, source_chunks
    
    except Exception as e:
        logger.error(f"Error in RAG pipeline query: {str(e)}")
        return f"An error occurred while processing your query: {str(e)}", []
