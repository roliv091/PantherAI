from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

class TaskItem(BaseModel):
    title: str
    due: Optional[str] = None
    weight: Optional[float] = None

class IngestResponse(BaseModel):
    ok: bool
    tasks: List[TaskItem] = []
    text_len: Optional[int] = None
    error: Optional[str] = None

class FinanceSummary(BaseModel):
    ok: bool
    totals: Dict[str, float]
    roundups: float
    runway_days: int
    error: Optional[str] = None
