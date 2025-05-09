import os
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
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
        openai_api_key = os.environ.get("OPENAI_API_KEY", "default-key")
        llm = OpenAI(temperature=0.5, api_key=openai_api_key)
        
        # Create a prompt template
        prompt_template = """
        You are an AI assistant specialized in market matching.
        Use the following context to answer the question.
        If you don't know the answer, just say "I don't have enough information to answer this question."
        
        Context:
        {context}
        
        Question:
        {question}
        
        Please provide a detailed market-oriented answer:
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
        
        return qa_chain
    
    except Exception as e:
        logger.error(f"Error initializing RAG pipeline: {str(e)}")
        raise

def query_rag_pipeline(query_text):
    """Process a query through the RAG pipeline and return the response with sources"""
    try:
        # Get embeddings for the query
        embedding_model = get_embeddings()
        query_embedding = embedding_model.embed_query(query_text)
        
        # Get vector store
        vector_store = get_vector_store()
        
        # Search for relevant document chunks
        search_results = vector_store.similarity_search_with_score(query_text, k=5)
        
        # Extract document chunks and relevance scores
        source_chunks = []
        context_texts = []
        
        for doc, score in search_results:
            # Assuming the document metadata contains the chunk ID
            chunk_id = doc.metadata.get('chunk_id')
            if chunk_id:
                source_chunks.append((chunk_id, float(score)))
                context_texts.append(doc.page_content)
        
        # If no source chunks were found, return a default response
        if not source_chunks:
            return "I don't have enough information to answer this question.", []
        
        # Create context from the retrieved chunks
        context = "\n\n".join(context_texts)
        
        # Initialize the RAG chain
        qa_chain = initialize_rag_pipeline()
        
        # Run the query through the chain
        response = qa_chain({"query": query_text})
        
        return response['result'], source_chunks
    
    except Exception as e:
        logger.error(f"Error in RAG pipeline query: {str(e)}")
        return f"An error occurred while processing your query: {str(e)}", []
