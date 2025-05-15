import os
import tempfile
from fastapi import UploadFile

async def save_temp_file(upload_file: UploadFile):
    try:
        suffix = os.path.splitext(upload_file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await upload_file.read()
            temp_file.write(content)
            return temp_file.name
    except Exception as e:
        raise IOError(f"File save failed: {str(e)}")