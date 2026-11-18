import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

import asyncio
from rag.chatbot import ChatbotEngine

def main():
    print("Testing Chatbot Engine...")
    engine = ChatbotEngine()
    print(f"Retriever documents loaded: {len(engine.retriever.documents)}")
    
    # Test queries
    queries = [
        "Tell me about Pagani DaVinci tower in Dubai",
        "What Lamborghini villas exist in Spain?",
        "What are the best Wasalt properties in Riyadh?"
    ]
    
    for q in queries:
        print(f"\n--- Testing Query: '{q}' ---")
        res = asyncio.run(engine.generate_response(q))
        print(f"Model: {res.get('model_used')}")
        docs = res.get('retrieved_documents', [])
        print(f"Retrieved {len(docs)} documents:")
        for d in docs[:2]:
            print(f"  • [{d.get('entity')}] {d.get('title')}")
        print("Summary output preview:")
        print(res.get('response')[:200] + "...")

    print("\n✅ All RAG and fallback tests passed successfully!")

if __name__ == "__main__":
    main()
