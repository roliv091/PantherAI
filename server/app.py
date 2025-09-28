from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path
import os
import PyPDF2
import io
from typing import Dict, Any

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=True)

# Import tools
from tools.gemini_router import chat as gemini_chat
from tools.campus_rag import add_document
from tools.syllabus_parser import parse_pdf

app = Flask(__name__)
CORS(app)

# Check for required environment variables
if not os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY') == 'your_api_key_here':
    print("WARNING: GEMINI_API_KEY not set. Chat functionality will be limited.")

# In-memory storage for tasks
_tasks = []

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"ok": True, "backend": "flask"})

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Chat endpoint powered by Gemini + RAG"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"ok": False, "error": "Message is required"}), 400
        
        message = data['message']
        result = gemini_chat(message)
        
        return jsonify({
            "ok": True,
            "answer": result["answer"],
            "sources": result["sources"]
        })
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/ingest/campus-doc', methods=['POST'])
def ingest_campus_doc():
    """Ingest campus document (PDF)"""
    try:
        if 'file' not in request.files:
            return jsonify({"ok": False, "error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"ok": False, "error": "No file selected"}), 400
        
        # Save file temporarily
        filename = file.filename
        file_path = f"/tmp/{filename}"
        file.save(file_path)
        
        # Extract text from PDF
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        # Add to RAG system
        add_document(text, filename)
        
        # Parse tasks
        tasks = parse_pdf(file_path)
        _tasks.extend(tasks)
        
        # Clean up
        os.remove(file_path)
        
        return jsonify({
            "ok": True,
            "tasks": tasks
        })
        
    except Exception as e:
        print(f"Ingest error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/ingest/vision', methods=['POST'])
def ingest_vision():
    """Ingest image using Gemini vision"""
    try:
        if 'file' not in request.files:
            return jsonify({"ok": False, "error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"ok": False, "error": "No file selected"}), 400
        
        # For now, just return a placeholder response
        # In a real implementation, you would use Gemini's vision API
        return jsonify({
            "ok": True,
            "text_len": 0,
            "tasks": []
        })
        
    except Exception as e:
        print(f"Vision ingest error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/finance/upload', methods=['POST'])
def finance_upload():
    """Finance upload endpoint - Coming Soon"""
    return jsonify({
        "ok": False,
        "error": "Finance feature coming soon! This will support CSV and PDF uploads for expense tracking."
    }), 501

@app.route('/finance/summary', methods=['GET'])
def finance_summary():
    """Finance summary endpoint - Coming Soon"""
    return jsonify({
        "ok": False,
        "error": "Finance feature coming soon! This will provide expense summaries, roundups, and runway calculations."
    }), 501

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Get recently parsed tasks"""
    return jsonify({"ok": True, "tasks": _tasks})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
