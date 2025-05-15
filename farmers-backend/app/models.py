from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.utils.database import Base

class Farmer(Base):
    __tablename__ = "farmers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100))
    phone = Column(String(20), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    raw_text = Column(Text)
    structured_data = Column(JSON)
    profile_text = Column(Text)
    status = Column(String(20), default="draft")
    embedding = Column(Vector(384))  # For all-MiniLM-L6-v2 model
    created_at = Column(DateTime(timezone=True), server_default=func.now())