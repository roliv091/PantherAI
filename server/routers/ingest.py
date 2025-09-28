# FastAPI ingest router (unused, kept for reference)
from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/campus-doc")
async def ingest_campus_doc(file: UploadFile = File(...)):
    # Implementation would go here
    pass

@router.post("/vision")
async def ingest_vision(file: UploadFile = File(...)):
    # Implementation would go here
    pass
