"""
Knowledge Base Builder
Consolidates DarGlobal and Wasalt real estate data, corporate intelligence,
and investment guides into an indexed knowledge store for the RAG engine.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("KnowledgeBaseBuilder")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

CORPORATE_OVERVIEW = [
    {
        "id": "kb-darglobal-overview",
        "entity": "DarGlobal PLC",
        "title": "About DarGlobal: The World's Premier Branded Real Estate Developer",
        "category": "Corporate Overview",
        "content": (
            "DarGlobal PLC is an international ultra-luxury real estate developer listed on the London Stock Exchange (LSE: DAR). "
            "It is the international luxury subsidiary of Dar Al Arkan, the premier Saudi Arabian real estate development group founded in 1994. "
            "DarGlobal specializes in creating bespoke trophy assets in the world's most desirable second-home and luxury destinations, "
            "including Dubai (UAE), Muscat (Oman), Marbella (Spain), Lusail (Qatar), and Shropshire (United Kingdom). "
            "DarGlobal is globally distinguished for pioneering luxury co-branding partnerships with iconic high-fashion, automotive, and hospitality maisons, "
            "including Automobili Lamborghini, Pagani Automobili, Missoni Home, Elie Saab, W Hotels (Marriott), Dolce & Gabbana, and The Trump Organization. "
            "Properties are designed for high-net-worth global investors seeking capital appreciation, prime yields, and lifestyle privileges."
        ),
        "tags": ["darglobal", "lse", "luxury", "developer", "dubai", "spain", "oman", "qatar", "uk", "pagani", "lamborghini", "trump"]
    },
    {
        "id": "kb-wasalt-overview",
        "entity": "Wasalt",
        "title": "About Wasalt: Saudi Arabia's Leading PropTech Real Estate Marketplace",
        "category": "Corporate Overview",
        "content": (
            "Wasalt (wasalt.sa) is a next-generation PropTech real estate platform in the Kingdom of Saudi Arabia, established as a strategic joint venture "
            "between Dar Al Arkan and Quara Holding. Officially licensed by the Real Estate General Authority (REGA), Wasalt serves as the central digital ecosystem "
            "connecting buyers, sellers, brokers, and institutional developers. "
            "Wasalt offers comprehensive verified listings across residential villas, apartments, commercial towers, and master-planned communities in Riyadh, "
            "Jeddah, Dammam, Al Khobar, Makkah, and Medina. Key innovations include AI-driven property valuation, 3D interactive community maps, "
            "off-plan project discovery, and the official Wasalt Electronic Auctions portal, which operates in coordination with the Entrustment and Liquidation Center (Infath) "
            "for transparent judicial and corporate asset liquidations."
        ),
        "tags": ["wasalt", "saudi arabia", "riyadh", "jeddah", "dar al arkan", "quara", "rega", "infath", "auctions", "proptech", "listings"]
    },
    {
        "id": "kb-relationship-overview",
        "entity": "DarGlobal & Wasalt Synergy",
        "title": "Synergy Between Dar Al Arkan, DarGlobal, and Wasalt",
        "category": "Corporate Overview",
        "content": (
            "Dar Al Arkan Real Estate Development Company (Saudi Joint Stock Company listed on Tadawul: 4300) is the foundational parent of both DarGlobal and Wasalt. "
            "While DarGlobal focuses on international ultra-luxury trophy residences across Europe, the GCC, and UK for global high-net-worth investors, "
            "Wasalt powers the domestic Saudi real estate ecosystem and digital transaction infrastructure under Vision 2030. "
            "Wasalt features Dar Al Arkan's master developments (such as Shams Ar Riyadh, Parisiana, Al Qasr) as well as showcase listings for high-profile international collaborations "
            "like Trump Tower Jeddah."
        ),
        "tags": ["dar al arkan", "darglobal", "wasalt", "tadawul", "vision 2030", "ecosystem", "real estate"]
    }
]

def build_knowledge_base():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Load DarGlobal Properties
    dg_file = DATA_DIR / "darglobal_properties.json"
    dg_props = []
    if dg_file.exists():
        with open(dg_file, "r", encoding="utf-8") as f:
            dg_props = json.load(f)
    
    # 2. Load Wasalt Properties
    ws_file = DATA_DIR / "wasalt_properties.json"
    ws_props = []
    if ws_file.exists():
        with open(ws_file, "r", encoding="utf-8") as f:
            ws_props = json.load(f)
            
    documents: List[Dict[str, Any]] = []
    
    # Add corporate overviews
    for doc in CORPORATE_OVERVIEW:
        documents.append({
            "id": doc["id"],
            "type": "corporate_guide",
            "title": doc["title"],
            "entity": doc["entity"],
            "text": f"{doc['title']}\n{doc['content']}",
            "metadata": {
                "category": doc["category"],
                "tags": doc["tags"]
            }
        })
        
    # Process DarGlobal Properties
    for p in dg_props:
        amenities_str = ", ".join(p.get("key_amenities", []))
        units_str = ", ".join(p.get("unit_types", []))
        content = (
            f"Property Name: {p['name']}\n"
            f"Developer: {p['developer']} (International Ultra-Luxury Portfolio)\n"
            f"Brand Partner: {p.get('brand_partner', 'DarGlobal Signature')}\n"
            f"Location: {p['location']}, {p['city']}, {p['country']}\n"
            f"Category: {p.get('category', 'Luxury Residences')}\n"
            f"Starting Price: {p.get('price_starting', 'Contact for Price')} (Approx: {p.get('price_usd_approx', 'N/A')})\n"
            f"Available Units: {units_str}\n"
            f"Status: {p.get('completion_status', 'Available')}\n"
            f"Overview: {p.get('description', '')}\n"
            f"Key Luxury Amenities: {amenities_str}\n"
            f"Investment Highlights: {p.get('investment_highlights', '')}\n"
            f"Official Link: {p.get('website_url', '')}"
        )
        documents.append({
            "id": p["id"],
            "type": "property",
            "entity": "DarGlobal",
            "title": p["name"],
            "text": content,
            "metadata": {
                "name": p["name"],
                "developer": "DarGlobal",
                "brand_partner": p.get("brand_partner", ""),
                "country": p.get("country", ""),
                "city": p.get("city", ""),
                "price": p.get("price_starting", ""),
                "price_usd": p.get("price_usd_approx", ""),
                "url": p.get("website_url", ""),
                "category": p.get("category", ""),
                "amenities": p.get("key_amenities", [])
            }
        })

    # Process Wasalt Properties
    for w in ws_props:
        amenities_str = ", ".join(w.get("key_amenities", []))
        units_str = ", ".join(w.get("unit_types", []))
        content = (
            f"Property Name: {w['name']}\n"
            f"Platform: Wasalt.sa (Saudi PropTech Marketplace)\n"
            f"Developer/Provider: {w.get('developer', 'Wasalt Verified Partner')}\n"
            f"Location: {w['location']}, {w['city']}, {w['country']}\n"
            f"Category: {w.get('category', 'Residential/Commercial')}\n"
            f"Starting Price: {w.get('price_starting', 'Contact for Price')} (Approx: {w.get('price_usd_approx', 'N/A')})\n"
            f"Available Units: {units_str}\n"
            f"Status: {w.get('completion_status', 'Available')}\n"
            f"Overview: {w.get('description', '')}\n"
            f"Key Amenities & Highlights: {amenities_str}\n"
            f"Investment Highlights: {w.get('investment_highlights', '')}\n"
            f"Official Link: {w.get('website_url', '')}"
        )
        documents.append({
            "id": w["id"],
            "type": "property",
            "entity": "Wasalt",
            "title": w["name"],
            "text": content,
            "metadata": {
                "name": w["name"],
                "developer": w.get("developer", "Wasalt Partner"),
                "country": w.get("country", "Saudi Arabia"),
                "city": w.get("city", "Riyadh"),
                "price": w.get("price_starting", ""),
                "price_usd": w.get("price_usd_approx", ""),
                "url": w.get("website_url", ""),
                "category": w.get("category", ""),
                "amenities": w.get("key_amenities", [])
            }
        })

    kb_payload = {
        "version": "1.0",
        "total_documents": len(documents),
        "documents": documents
    }

    out_file = DATA_DIR / "knowledge_base.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(kb_payload, f, indent=2, ensure_ascii=False)

    logger.info(f"Knowledge base successfully created at {out_file} with {len(documents)} indexed documents.")
    return kb_payload

if __name__ == "__main__":
    build_knowledge_base()

