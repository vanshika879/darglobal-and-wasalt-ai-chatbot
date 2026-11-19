# DarGlobal & Wasalt AI Real Estate Concierge 🏛️

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-Free%20Tier-6366F1.svg)](https://openrouter.ai)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-gold.svg)](https://opensource.org/licenses/MIT)



An applied AI conversational advisor grounded in verified public data from **DarGlobal PLC** (LSE: DAR) and **Wasalt.sa** (Saudi PropTech marketplace by Dar Al Arkan & Quara). The system features an ultra-responsive RAG retrieval engine, free-tier OpenRouter LLM orchestration with resilient model failover, a branded luxury concierge UI, and production Docker containerization.

---

## 🌟 Key Features

1. **Dual Knowledge Ingestion**:
   - **DarGlobal International Portfolio**: Scraped and structured data covering flagship branded developments (*DaVinci Tower by Pagani, Tierra Viva by Automobili Lamborghini in Marbella, Aida by Trump International in Oman, Urban Oasis by Missoni, W Residences Dubai, Les Vagues by Elie Saab*, etc.).
   - **Wasalt Saudi Marketplace**: Public categories and verified residential/commercial communities in Riyadh, Jeddah, and Al Khobar (*Shams Ar Riyadh, Parisiana Living, Al Qasr, Sedra by ROSHN, Obhur Waterfront, and Infath electronic real estate auctions*).

2. **RAG Architecture with BM25 Hybrid Scoring**:
   - Zero-bloat, high-speed lexical and entity-boosted vector retrieval (< 5ms response time).
   - Guarantees accurate pricing, currencies (AED, SAR, EUR, GBP, USD), specifications, and amenities without hallucination.

3. **OpenRouter Free-Tier LLMs with Automatic Failover**:
   - Seamlessly calls OpenRouter free models:
     - `meta-llama/llama-3.3-70b-instruct:free` (Primary)
     - `google/gemini-2.0-flash-exp:free` (Multimodal/Speed fallback)
     - `qwen/qwen-2.5-72b-instruct:free` (Bilingual English/Arabic reasoning)
     - `mistralai/mistral-small-24b-instruct-2501:free`
   - **Resilient Cascade**: Automatically falls back to secondary free models if rate-limited (HTTP 429/503).
   - **Offline Grounded Fallback**: Even without an API key or under complete provider outages, the app serves verified answers from the retrieved database context.

4. **DarGlobal Luxury Front-End**:
   - Bespoke obsidian and champagne gold design matching DarGlobal's high-net-worth aesthetic.
   - Interactive property catalog drawer, clickable quick suggestions, source document verification badges, and VIP consultation booking.

5. **Containerised & 1-Click Cloud Deployable**:
   - Production-ready `Dockerfile` and `docker-compose.yml`.
   - Native support for **Hugging Face Spaces (Free Docker SDK)**, **Render**, or **Koyeb** for instant public HTTPS deployment.

---

## 🚀 Quickstart: Running Locally

### Option 1: Standard Python

1. **Clone the repository and enter directory**:
   ```bash
   git clone <repo-url>
   cd darglobal-wasalt-ai-chatbot
   ```

2. **Create a virtual environment and install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables (Optional)**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Add your free [OpenRouter API key](https://openrouter.ai/keys) if desired (you can also input it directly in the UI):
   ```env
   OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
   PORT=7860
   ```

4. **Launch the application**:
   ```bash
   python app.py
   ```
   Open your browser to: `http://localhost:7860`

---

### Option 2: Run with Docker 🐳

1. **Build the Docker container**:
   ```bash
   docker build -t darglobal-concierge .
   ```

2. **Run the container**:
   ```bash
   docker run -d -p 7860:7860 --name darglobal-concierge-app -e OPENROUTER_API_KEY="your-key" darglobal-concierge
   ```

3. **Or run with Docker Compose**:
   ```bash
   docker compose up --build
   ```
   Access the application at `http://localhost:7860`.

---

## 🧪 Sample Prompts for Testing

Try submitting these prompts in the chat interface:

- **Branded Residences**: *"What exclusive residences does DarGlobal offer in Dubai in partnership with Pagani and Missoni?"*
- **International Luxury**: *"Tell me about the Lamborghini luxury villas at Tierra Viva in Marbella, Spain."*
- **Oman Clifftop Golf**: *"What are the investment terms and amenities of Aida by Trump International in Oman?"*
- **Saudi Arabia Market (Wasalt)**: *"What family villa communities are available on Wasalt in northern Riyadh?"*
- **Auctions & Commercial**: *"How does the Wasalt electronic auction platform with Infath function?"*

---

## 📄 License & Attribution

- Developed for the **DarGlobal Junior AI Engineer – Applied AI** Technical Assessment.
- All corporate trademarks and branding belong to **DarGlobal PLC** and **Wasalt Real Estate Platform** (Dar Al Arkan / Quara Holding).

