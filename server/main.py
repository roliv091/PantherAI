# FastAPI health check (unused, kept for reference)
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"ok": True, "backend": "fastapi"}
