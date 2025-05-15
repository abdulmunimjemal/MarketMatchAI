import os
import tempfile
import fitz  # PyMuPDF
from docx import Document
from PIL import Image
import pytesseract
from openai import OpenAI
from app.models import FarmerProfile
from app.utils.file_processing import save_temp_file

client = OpenAI()

async def process_uploaded_file(farmer_id: int, file_type: str, file: UploadFile, db):
    text = ""
    file_ext = file.filename.split('.')[-1].lower()
    
    # Save file to temporary location
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        if file_type == "audio":
            # Transcribe audio using Whisper
            with open(temp_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            text = transcript.text
            
        elif file_type == "document":
            if file_ext == "pdf":
                doc = fitz.open(temp_path)
                text = " ".join([page.get_text() for page in doc])
            elif file_ext in ["docx", "doc"]:
                doc = Document(temp_path)
                text = " ".join([para.text for para in doc.paragraphs])
                
        elif file_type == "image":
            img = Image.open(temp_path)
            text = pytesseract.image_to_string(img)
            
        # Store raw text and process with LLM
        structured_data = extract_structured_data(text)
        
        # Update or create profile
        profile = db.query(FarmerProfile).filter(
            FarmerProfile.farmer_id == farmer_id
        ).first()
        
        if not profile:
            profile = FarmerProfile(farmer_id=farmer_id)
            db.add(profile)
            
        profile.raw_text = text
        profile.structured_data = structured_data
        db.commit()
        
        return {"text_extracted": text[:500] + "..."}  # Return snippet
    
    finally:
        os.remove(temp_path)