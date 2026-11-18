"""
OpenRouter RAG Chatbot Engine
Manages conversation state, context augmentation with DarGlobal and Wasalt real estate data,
and resilient multi-model failover for OpenRouter free-tier LLMs.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx
from dotenv import load_dotenv

from .vector_search import RealEstateRetriever

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
logger = logging.getLogger("ChatbotEngine")

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Primary free-tier models on OpenRouter with automatic failover
FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "mistralai/mistral-small-24b-instruct-2501:free",
    "deepseek/deepseek-r1:free"
]

SYSTEM_PROMPT = """You are the official AI Luxury Real Estate Concierge for DarGlobal and Wasalt.

DarGlobal PLC (LSE: DAR) is the international ultra-luxury real estate developer originating from Saudi Arabia's Dar Al Arkan (est. 1994). DarGlobal creates iconic trophy residences across Dubai, Spain, Oman, Qatar, and the UK in collaboration with global luxury houses:
- Automobili Lamborghini (Tierra Viva villas in Marbella, Spain)
- Pagani Automobili (DaVinci Tower in Downtown Dubai)
- Missoni Home (Urban Oasis in Dubai Canal & Marea in Spain)
- The Trump Organization (Aida clifftop golf resort in Oman & Trump Tower Jeddah)
- W Hotels / Marriott (W Residences Dubai Harbour)
- Elie Saab (Les Vagues in Qatar)

Wasalt (wasalt.sa) is Saudi Arabia's leading PropTech real estate platform, backed by Dar Al Arkan and Quara Holding, licensed by REGA. It is the premier digital marketplace for verified residential communities (Shams Ar Riyadh, Parisiana Living, Al Qasr), luxury villas, off-plan projects, and electronic judicial/corporate auctions in partnership with Infath.

Instructions:
1. Ground your answers in the provided RETRIEVED CONTEXT below. Accurately state property names, developer affiliations, locations, prices, currencies, and signature amenities.
2. Maintain an elegant, sophisticated, and helpful concierge tone (like a private wealth real estate advisor).
3. If the user asks in Arabic, answer in fluent, polished Arabic (فصحى راقية). If in English, answer in polished English.
4. When highlighting properties, mention their investment appeal (e.g., rental yields, Golden Visa eligibility in Spain/Oman, prime locations).
5. Always offer to help the client schedule a private consultation, request an official brochure, or connect with a DarGlobal / Wasalt private advisor.
"""

class ChatbotEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.retriever = RealEstateRetriever()

    def set_api_key(self, api_key: str):
        self.api_key = api_key.strip()

    def _format_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        if not retrieved_docs:
            return "No specific property records retrieved."

        chunks = []
        for i, doc in enumerate(retrieved_docs, start=1):
            chunks.append(f"--- [DOCUMENT {i}: {doc.get('title', 'Unknown')}] ---\n{doc.get('text', '')}")
        return "\n\n".join(chunks)

    async def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        model_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrates retrieval and OpenRouter generation with model failover.
        """
        if conversation_history is None:
            conversation_history = []

        # 1. Retrieve most relevant DarGlobal / Wasalt context
        relevant_docs = self.retriever.retrieve(user_message, top_k=4)
        context_str = self._format_context(relevant_docs)

        # 2. Build prompt payload
        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nRETRIEVED CONTEXT FROM DATABASE:\n{context_str}"}
        ]
        
        # Append recent history (up to last 6 turns)
        for turn in conversation_history[-6:]:
            if turn.get("role") in ["user", "assistant"]:
                messages.append({"role": turn["role"], "content": turn["content"]})

        messages.append({"role": "user", "content": user_message})

        # 3. Model cascade
        candidate_models = [model_override] if model_override else FREE_MODELS

        # If no API key is available, generate a direct grounded response from retrieved context
        if not self.api_key:
            fallback_text = self._generate_grounded_summary(user_message, relevant_docs)
            return {
                "response": fallback_text,
                "model_used": "local-rag-grounded",
                "retrieved_documents": relevant_docs,
                "needs_api_key": True
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://darglobal-wasalt-concierge.internal",
            "X-Title": "DarGlobal-Wasalt AI Concierge"
        }

        last_error = None
        for model in candidate_models:
            if not model:
                continue
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.4,
                "max_tokens": 1024
            }
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(OPENROUTER_API_URL, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        reply = data["choices"][0]["message"]["content"]
                        return {
                            "response": reply,
                            "model_used": model,
                            "retrieved_documents": relevant_docs,
                            "needs_api_key": False
                        }
                    elif resp.status_code in (429, 503, 404):
                        logger.warning(f"Model {model} returned HTTP {resp.status_code}. Trying next model...")
                        last_error = f"Model {model} busy (HTTP {resp.status_code})"
                        continue
                    elif resp.status_code == 401:
                        logger.error("Invalid OpenRouter API Key provided.")
                        return {
                            "response": (
                                "Authentication failed with OpenRouter. Please provide a valid OpenRouter API key "
                                "using the **Settings** button in the top bar or via the `OPENROUTER_API_KEY` environment variable."
                            ),
                            "model_used": model,
                            "retrieved_documents": relevant_docs,
                            "needs_api_key": True,
                            "error": "HTTP 401 Unauthorized"
                        }
                    else:
                        last_error = f"HTTP {resp.status_code}: {resp.text}"
            except Exception as e:
                logger.warning(f"Error calling model {model}: {e}. Retrying with next model...")
                last_error = str(e)

        # Fallback if all models failed or timed out
        grounded_reply = self._generate_grounded_summary(user_message, relevant_docs)
        return {
            "response": grounded_reply,
            "model_used": "rag-grounded-fallback",
            "retrieved_documents": relevant_docs,
            "error_note": f"OpenRouter free models temporarily busy ({last_error}). Served via local verified RAG context."
        }

    def _generate_grounded_summary(self, query: str, docs: List[Dict[str, Any]]) -> str:
        """Deterministic context-grounded response when API key is missing or models are at capacity."""
        if not docs:
            return (
                "Thank you for contacting the DarGlobal & Wasalt Real Estate Concierge. "
                "I specialize in luxury residences from DarGlobal (Dubai, Spain, Oman, Qatar, UK) "
                "and premium properties across Saudi Arabia via Wasalt. "
                "Please specify a destination, branded project, or investment preference."
            )

        top_doc = docs[0]
        meta = top_doc.get("metadata", {})
        title = top_doc.get("title", "")
        entity = top_doc.get("entity", "")
        price = meta.get("price", "Inquire for pricing")
        country = meta.get("country", "")
        city = meta.get("city", "")
        amenities = meta.get("amenities", [])

        lines = [
            f"### **{title}** ({entity})",
            f"**Location:** {city}, {country}" if city else "",
            f"**Starting Price:** {price}" if price else "",
            "",
            top_doc.get("text", "")[:450] + "...",
            "",
            "**Key Highlights & Amenities:**"
        ]
        for a in amenities[:4]:
            lines.append(f"- {a}")

        lines.append("\n*Would you like to schedule a private advisory consultation or view floor plans?*")
        return "\n".join([line for line in lines if line])
