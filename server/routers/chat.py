# FastAPI chat router (unused, kept for reference)
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Implementation would go here
    pass
