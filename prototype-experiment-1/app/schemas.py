from pydantic import BaseModel
from typing import Optional, List

class FarmerCreate(BaseModel):
    name: str
    location: str
    phone: str

class FileUpload(BaseModel):
    file_type: str  # audio|document|image
    description: Optional[str] = None

class FarmerProfileResponse(BaseModel):
    id: int
    name: str
    location: str
    profile_text: str
    status: str

class SearchQuery(BaseModel):
    text: str
    filters: Optional[dict] = None
    top_k: int = 10

class SearchResult(BaseModel):
    farmer_id: int
    name: str
    location: str
    similarity_score: float
    profile_summary: str
    raw_text_snippet: str