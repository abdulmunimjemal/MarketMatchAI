from sentence_transformers import SentenceTransformer
from app.models import FarmerProfile
from sqlalchemy.orm import Session

model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embeddings(text: str):
    return model.encode(text).tolist()

def hybrid_search(db: Session, query: str, filters: dict = None, top_k: int = 10):
    # Generate query embedding
    query_embedding = generate_embeddings(query)
    
    # Base query
    base_query = db.query(FarmerProfile).filter(
        FarmerProfile.status == "approved"
    )
    
    # Apply filters
    if filters:
        for key, value in filters.items():
            base_query = base_query.filter(
                FarmerProfile.structured_data[key].astext == str(value)
            )
    
    # Vector similarity search
    results = base_query.order_by(
        FarmerProfile.embedding.l2_distance(query_embedding)
    ).limit(top_k).all()
    
    # Format results
    return [{
        "farmer_id": profile.farmer_id,
        "name": profile.farmer.name,
        "location": profile.farmer.location,
        "similarity_score": float(profile.embedding.l2_distance(query_embedding)),
        "profile_summary": profile.profile_text[:200] + "...",
        "raw_text_snippet": profile.raw_text[:200] + "..."
    } for profile in results]