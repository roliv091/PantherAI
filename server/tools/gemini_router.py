import google.generativeai as genai
from typing import Dict, Any

# Dual import support for Flask and FastAPI
try:
    from ..config import settings
except ImportError:
    from config import settings

from .campus_rag import query as rag_query

# Configure Gemini
print(f"Configuring Gemini with API key: {settings.GEMINI_API_KEY[:20]}...")
genai.configure(api_key=settings.GEMINI_API_KEY)
_model = genai.GenerativeModel("gemini-2.5-flash")
print("Gemini model configured successfully")

def chat(user_msg: str) -> Dict[str, Any]:
    """Chat with Gemini using RAG context"""
    # Get relevant context from RAG
    rag = rag_query(user_msg, k=4)
    
    # Build context string
    context_items = []
    for item in rag["items"]:
        context_items.append(f"[Source: {item['source']}]\n{item['text']}")
    
    context = "\n\n".join(context_items) if context_items else "(no context)"
    
    # Create prompt
    prompt = (
        "You are PantherAI, an FIU campus copilot. Use context when helpful and cite sources used.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {user_msg}\n\n"
        "If you used context, list source names at the end with 'Sources:'"
    )
    
    try:
        resp = _model.generate_content(prompt)
        answer = (resp.text or "").strip() or "(no response)"
        
        return {
            "answer": answer,
            "sources": [item["source"] for item in rag["items"]]
        }
    except Exception as e:
        return {
            "answer": f"Error generating response: {str(e)}",
            "sources": []
        }
