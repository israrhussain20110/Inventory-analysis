import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from services.metrics import check_data_status
from models import DataStatusResponse
from database import insert_data, db
import pandas as pd
import io
import io

router = APIRouter()

ALLOWED_COLLECTIONS = ["retail_data"]

@router.post("/upload/{collection_name}")
async def upload_data(collection_name: str, file: UploadFile = File(...)):
    """
    Uploads a CSV file to the specified collection.
    Note: This endpoint will delete all existing data in the collection before inserting the new data.
    TODO: For very large files, a streaming approach would be more memory-efficient.
    """
    if collection_name not in ALLOWED_COLLECTIONS:
        raise HTTPException(400, detail=f"Invalid collection name: {collection_name}. Allowed collections are: {', '.join(ALLOWED_COLLECTIONS)}")

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
async def get_data_status():
    count = db["retail_data"].estimated_document_count()
    return {"collection": "retail_data", "record_count": count, "is_loaded": count > 0}