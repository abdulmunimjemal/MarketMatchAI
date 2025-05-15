from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.models import Farmer, FarmerProfile
from app.schemas import FarmerCreate, FarmerProfileResponse, FileUpload
from app.utils.database import get_db
from app.services.ingestion import process_uploaded_file
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/")
async def create_farmer(farmer: FarmerCreate, db: Session = Depends(get_db)):
    db_farmer = Farmer(**farmer.dict())
    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    return db_farmer

@router.post("/{farmer_id}/uploads")
async def upload_files(
    farmer_id: int,
    file_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Save file temporarily and process
        result = await process_uploaded_file(farmer_id, file_type, file, db)
        return {"message": "File processed successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{farmer_id}/profile", response_model=FarmerProfileResponse)
async def get_profile(farmer_id: int, db: Session = Depends(get_db)):
    profile = db.query(FarmerProfile).filter(
        FarmerProfile.farmer_id == farmer_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile