"""
FastAPI Server for DarGlobal & Wasalt AI Real Estate Concierge
Exposes conversational RAG endpoints, property directory, and serves the luxury web UI.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from rag.chatbot import ChatbotEngine, FREE_MODELS

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

app = FastAPI(
    title="DarGlobal & Wasalt AI Real Estate Concierge",
    description="Applied AI Chatbot powered by OpenRouter free-tier LLMs and grounded in DarGlobal and Wasalt real estate data.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and Templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Global Chatbot Engine Instance
chatbot_engine = ChatbotEngine()

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []
    model: Optional[str] = None
    api_key: Optional[str] = None

class LeadRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    property_interest: Optional[str] = None
    notes: Optional[str] = None

@app.get("/")
async def root(request: Request):
    """Serves the main luxury concierge interface."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "free_models": FREE_MODELS,
        "default_model": FREE_MODELS[0]
    })

@app.get("/api/health")
async def health_check():
    """Health and status endpoint."""
    kb_path = DATA_DIR / "knowledge_base.json"
    doc_count = 0
    if kb_path.exists():
        with open(kb_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            doc_count = len(data.get("documents", []))

    has_env_key = bool(os.getenv("OPENROUTER_API_KEY", "").strip())
    return {
        "status": "healthy",
        "service": "DarGlobal & Wasalt AI Real Estate Concierge",
        "indexed_documents": doc_count,
        "free_models_supported": FREE_MODELS,
        "env_api_key_configured": has_env_key
    }

@app.post("/api/chat")
async def chat_endpoint(payload: ChatRequest):
    """Handles conversational queries using RAG and OpenRouter."""
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    engine = chatbot_engine
    if payload.api_key and payload.api_key.strip():
        engine = ChatbotEngine(api_key=payload.api_key.strip())

    result = await engine.generate_response(
        user_message=payload.message,
        conversation_history=payload.history,
        model_override=payload.model
    )
    return result

@app.get("/api/properties")
async def get_properties(
    developer: Optional[str] = None,
    city: Optional[str] = None,
    country: Optional[str] = None
):
    """Returns curated properties from DarGlobal and Wasalt with filtering."""
    dg_path = DATA_DIR / "darglobal_properties.json"
    ws_path = DATA_DIR / "wasalt_properties.json"

    all_properties = []
    if dg_path.exists():
        with open(dg_path, "r", encoding="utf-8") as f:
            all_properties.extend(json.load(f))
    if ws_path.exists():
        with open(ws_path, "r", encoding="utf-8") as f:
            all_properties.extend(json.load(f))

    filtered = all_properties
    if developer:
        dev_lower = developer.lower()
        filtered = [p for p in filtered if dev_lower in p.get("developer", "").lower()]
    if city:
        city_lower = city.lower()
        filtered = [p for p in filtered if city_lower in p.get("city", "").lower()]
    if country:
        country_lower = country.lower()
        filtered = [p for p in filtered if country_lower in p.get("country", "").lower()]

    return {
        "total": len(filtered),
        "properties": filtered
    }

@app.post("/api/lead")
async def capture_lead(lead: LeadRequest):
    """Simulates VIP consultation and lead capture."""
    leads_file = DATA_DIR / "leads.json"
    leads = []
    if leads_file.exists():
        try:
            with open(leads_file, "r", encoding="utf-8") as f:
                leads = json.load(f)
        except Exception:
            leads = []

    leads.append(lead.dict())
    with open(leads_file, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2)

    return {
        "status": "success",
        "message": "Consultation request received. A DarGlobal / Wasalt private client advisor will be in touch shortly."
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    print(f"Starting DarGlobal Concierge server on port {port}...")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
