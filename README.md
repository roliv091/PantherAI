# PantherAI - FIU Campus Copilot

A demo-ready app with campus Q&A, syllabus/task extraction, and personal finance summary features.

## Features

- **Chat endpoint** powered by Gemini 1.5 Pro + RAG over uploaded PDFs/images
- **PDF ingestion** for syllabus/campus docs with task extraction
- **Image processing** for syllabus/whiteboard photos with OCR
- **Finance tracking** with CSV upload and summary calculations
- **Modern UI** with Go-Blue style chat interface

## Quick Start

### Backend (Flask)

```bash
cd server
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
python app.py
# Server runs on http://127.0.0.1:8000
```

### Frontend (React)

```bash
cd app
npm install
npm run dev
# Frontend runs on http://localhost:3000 (or next available port)
```

## Environment Setup

1. Copy `server/.env` and add your Gemini API key:
```bash
GEMINI_API_KEY=your_actual_api_key_here
EMBED_MODEL=all-MiniLM-L6-v2
CHROMA_PATH=../data/chroma
```

## API Endpoints

- `GET /health` - Health check
- `POST /chat` - Chat with PantherAI
- `POST /ingest/campus-doc` - Upload PDF syllabus
- `POST /ingest/vision` - Upload image for OCR
- `POST /finance/upload` - Upload CSV transactions
- `GET /finance/summary` - Get finance summary
- `GET /tasks` - Get parsed tasks

## Project Structure

```
PantherAI/
├── server/                 # Flask backend
│   ├── app.py             # Main Flask app
│   ├── config.py          # Settings
│   ├── models.py          # Pydantic models
│   ├── tools/             # Core functionality
│   │   ├── campus_rag.py  # Document storage & search
│   │   ├── gemini_router.py # Gemini chat integration
│   │   ├── syllabus_parser.py # PDF task extraction
│   │   └── finance_math.py # Finance calculations
│   └── requirements.txt   # Python dependencies
├── app/                   # React frontend
│   ├── src/
│   │   ├── PantherUI.tsx  # Main chat interface
│   │   ├── api.ts         # API client
│   │   └── main.tsx       # App entry point
│   └── package.json       # Node dependencies
└── data/                  # Data storage
    ├── chroma/           # Vector database
    └── campus_docs/     # Uploaded documents
```

## Testing

The app is functional with simplified dependencies. Key endpoints tested:

- ✅ Health check: `curl http://127.0.0.1:8000/health`
- ✅ Chat endpoint: `curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d '{"message": "Hello!"}'`
- ✅ Finance summary: `curl http://127.0.0.1:8000/finance/summary`
- ✅ Tasks endpoint: `curl http://127.0.0.1:8000/tasks`

## Notes

- Uses in-memory storage for simplicity (no ChromaDB dependency issues)
- Requires valid Gemini API key for full chat functionality
- Frontend uses Tailwind CSS with Go-Blue color scheme
- All endpoints return JSON with `{"ok": true/false}` format
