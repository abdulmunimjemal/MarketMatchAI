from fastapi import APIRouter, Depends, HTTPException
from app.schemas import SearchQuery, SearchResult
from app.services.vector_db import hybrid_search
from app.utils.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/", response_model=list[SearchResult])
async def search_farmers(
    query: SearchQuery,
    db: Session = Depends(get_db)
):
    try:
        results = hybrid_search(db, query.text, query.filters, query.top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))