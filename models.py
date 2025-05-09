from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    documents = db.relationship('Document', backref='owner', lazy='dynamic')
    queries = db.relationship('Query', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    content_type = db.Column(db.String(64))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chunks = db.relationship('DocumentChunk', backref='document', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Document {self.filename}>'

class DocumentChunk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    chunk_index = db.Column(db.Integer, nullable=False)
    embedding_id = db.Column(db.String(128))
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    
    def __repr__(self):
        return f'<DocumentChunk {self.id} from Document {self.document_id}>'

class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    responses = db.relationship('Response', backref='query', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Query {self.id}>'

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    query_id = db.Column(db.Integer, db.ForeignKey('query.id'), nullable=False)
    source_chunks = db.relationship('ResponseSourceChunk', backref='response', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Response {self.id}>'

class ResponseSourceChunk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_chunk_id = db.Column(db.Integer, db.ForeignKey('document_chunk.id'), nullable=False)
    document_chunk = db.relationship('DocumentChunk')
    relevance_score = db.Column(db.Float)
    response_id = db.Column(db.Integer, db.ForeignKey('response.id'), nullable=False)
    
    def __repr__(self):
        return f'<ResponseSourceChunk {self.id}>'
