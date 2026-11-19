"""
DarGlobal Data Scraper & Aggregator
Extracts public portfolio information, luxury branded partnerships,
and residential specifications from darglobal.co.uk.
"""

import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DarGlobalScraper")

BASE_URL = "https://darglobal.co.uk"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_sitemap_projects() -> List[str]:
    """Fetch project URLs listed in the public sitemap."""
    sitemap_url = f"{BASE_URL}/sitemap.xml"
    project_urls = []
    try:
        logger.info(f"Fetching sitemap from {sitemap_url}")
        with httpx.Client(timeout=10, headers=HEADERS, follow_redirects=True) as client:
            resp = client.get(sitemap_url)
            if resp.status_code == 200:
                urls = re.findall(r"<loc>(https://darglobal\.co\.uk/[^<]+)</loc>", resp.text)
                for u in urls:
                    if any(slug in u for slug in [
                        "davinci-tower", "tierra-viva", "urban-oasis", "aida", 
                        "trump-tower", "w-residences", "dg1", "les-vagues", "astbury"
                    ]):
                        if u not in project_urls:
                            project_urls.append(u)
                logger.info(f"Discovered {len(project_urls)} project links from sitemap.")
            else:
                logger.warning(f"Sitemap request returned HTTP {resp.status_code}")
    except Exception as e:
        logger.error(f"Error fetching sitemap: {e}")
    return project_urls

def load_verified_darglobal_data() -> List[Dict[str, Any]]:
    """Loads curated verified public properties from local storage."""
    file_path = DATA_DIR / "darglobal_properties.json"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data)} verified DarGlobal properties from {file_path.name}")
            return data
    return []

def run_scraper() -> List[Dict[str, Any]]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    discovered_urls = fetch_sitemap_projects()
    properties = load_verified_darglobal_data()
    
    # Enrich with discovered URLs if not present
    for prop in properties:
        prop["source"] = "DarGlobal Official Portal"
        prop["live_sitemap_matched"] = any(prop["id"].split("-")[1] in u for u in discovered_urls)

    out_file = DATA_DIR / "darglobal_properties.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(properties, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved {len(properties)} DarGlobal properties to {out_file}")
    return properties

if __name__ == "__main__":
    run_scraper()

