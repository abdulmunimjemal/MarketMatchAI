import os
import json
import logging
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

from app import db
from models import User, Document, DocumentChunk, Query, Response, ResponseSourceChunk
from utils.document_processor import process_document
from utils.rag_pipeline import query_rag_pipeline

logger = logging.getLogger(__name__)

def register_routes(app):
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/documents')
    def documents():
        # Get all documents (for simplicity, no user auth in this MVP)
        all_documents = Document.query.all()
        return render_template('documents.html', documents=all_documents)
    
    @app.route('/query')
    def query_page():
        # Get recent queries
        recent_queries = Query.query.order_by(Query.timestamp.desc()).limit(5).all()
        return render_template('query.html', recent_queries=recent_queries)
    
    @app.route('/api/documents/upload', methods=['POST'])
    def upload_document():
        if 'document' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['document']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        filename = secure_filename(file.filename)
        
        # Create directory to save files if it doesn't exist
        upload_dir = os.path.join('uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file temporarily
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        try:
            # Read the content of the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create a document in the database
            # For MVP, assign to first user or create one if none exists
            user = User.query.first()
            if not user:
                user = User(username="demo_user", email="demo@example.com", password_hash=generate_password_hash("password"))
                db.session.add(user)
                db.session.commit()
            
            document = Document(
                filename=filename,
                title=filename,
                content=content,
                content_type='text',
                user_id=user.id
            )
            db.session.add(document)
            db.session.commit()
            
            # Process the document (create chunks, embeddings, etc.)
            process_document(document.id)
            
            # Remove temporary file
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'document_id': document.id,
                'filename': filename
            })
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/documents', methods=['GET'])
    def get_documents():
        try:
            documents = Document.query.all()
            document_list = [{
                'id': doc.id,
                'filename': doc.filename,
                'title': doc.title,
                'upload_date': doc.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
                'processed': doc.processed
            } for doc in documents]
            
            return jsonify({
                'success': True,
                'documents': document_list
            })
        except Exception as e:
            logger.error(f"Error fetching documents: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/documents/<int:document_id>', methods=['GET'])
    def get_document(document_id):
        try:
            document = Document.query.get(document_id)
            if not document:
                return jsonify({'error': 'Document not found'}), 404
            
            # Get chunks for this document
            chunks = DocumentChunk.query.filter_by(document_id=document_id).all()
            
            document_data = {
                'id': document.id,
                'filename': document.filename,
                'title': document.title,
                'content': document.content,
                'upload_date': document.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
                'processed': document.processed,
                'chunks': [{
                    'id': chunk.id,
                    'content': chunk.content[:100] + '...' if len(chunk.content) > 100 else chunk.content,
                    'chunk_index': chunk.chunk_index
                } for chunk in chunks]
            }
            
            return jsonify({
                'success': True,
                'document': document_data
            })
        except Exception as e:
            logger.error(f"Error fetching document: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/query', methods=['POST'])
    def process_query():
        try:
            data = request.json
            query_text = data.get('query')
            
            if not query_text:
                return jsonify({'error': 'Query text is required'}), 400
            
            # For MVP, assign to first user or create one if none exists
            user = User.query.first()
            if not user:
                user = User(username="demo_user", email="demo@example.com", password_hash=generate_password_hash("password"))
                db.session.add(user)
                db.session.commit()
            
            # Create query record
            query = Query(
                content=query_text,
                user_id=user.id
            )
            db.session.add(query)
            db.session.commit()
            
            # Process the query through RAG pipeline
            response_text, source_chunks = query_rag_pipeline(query_text)
            
            # Create response record
            response = Response(
                content=response_text,
                query_id=query.id
            )
            db.session.add(response)
            db.session.commit()
            
            # Add source chunks to the response
            for chunk_id, score in source_chunks:
                source = ResponseSourceChunk(
                    document_chunk_id=chunk_id,
                    relevance_score=score,
                    response_id=response.id
                )
                db.session.add(source)
            
            db.session.commit()
            
            # Prepare the response with sources
            source_documents = []
            for chunk_id, score in source_chunks:
                chunk = DocumentChunk.query.get(chunk_id)
                if chunk:
                    document = Document.query.get(chunk.document_id)
                    source_documents.append({
                        'document_title': document.title,
                        'chunk_content': chunk.content,
                        'relevance_score': score
                    })
            
            return jsonify({
                'success': True,
                'query_id': query.id,
                'response': response_text,
                'sources': source_documents
            })
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/queries', methods=['GET'])
    def get_queries():
        try:
            queries = Query.query.order_by(Query.timestamp.desc()).limit(10).all()
            query_list = [{
                'id': q.id,
                'content': q.content,
                'timestamp': q.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'responses': [{
                    'id': r.id,
                    'content': r.content[:100] + '...' if len(r.content) > 100 else r.content
                } for r in q.responses]
            } for q in queries]
            
            return jsonify({
                'success': True,
                'queries': query_list
            })
        except Exception as e:
            logger.error(f"Error fetching queries: {str(e)}")
            return jsonify({'error': str(e)}), 500
