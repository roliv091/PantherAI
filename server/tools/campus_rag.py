# Simple in-memory storage for documents (no ChromaDB for now)
from typing import List, Dict, Any
import re

# In-memory document storage
_documents = []

def add_document(text: str, source: str) -> None:
    """Add a document to the in-memory storage"""
    _documents.append({
        "text": text,
        "source": source
    })

def query(question: str, k: int = 4) -> Dict[str, Any]:
    """Simple keyword-based search"""
    question_lower = question.lower()
    results = []
    
    for doc in _documents:
        text_lower = doc["text"].lower()
        # Simple keyword matching
        if any(word in text_lower for word in question_lower.split()):
            results.append(doc)
    
    # Return top k results
    return {"items": results[:k]}
