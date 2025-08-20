import os
import sys
# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.services.metrics import check_data_status
from app.models import DataStatusResponse
from app.database import insert_data, get_data
import pandas as pd
import io
import io

router = APIRouter()

@router.post("/upload/{collection_name}")
async def upload_data(collection_name: str, file: UploadFile = File(...)):
    if file.content_type != 'text/csv':
        raise HTTPException(400, detail="Invalid document type")
    try:
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        data = df.to_dict('records')
        insert_data(data, collection_name)
        return {"message": f"Data uploaded successfully to {collection_name}"}
    except Exception as e:
        raise HTTPException(500, detail=f"Error processing file: {e}")

@router.get("/status")
async def get_data_status(db_data=Depends(get_data)):
    status = check_data_status(db_data)
    return DataStatusResponse(**status)