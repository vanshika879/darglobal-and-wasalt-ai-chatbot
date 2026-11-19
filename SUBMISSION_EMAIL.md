# DarGlobal Technical Assignment Submission Email

**To:** `careers@darglobal.co.uk`  
**Subject:** Application for Junior AI Engineer – Applied AI | Technical Assignment Submission – [Your Full Name]

---

Dear DarGlobal Talent Acquisition Team,

Thank you for the opportunity to complete the technical assessment for the **Junior AI Engineer – Applied AI** position at DarGlobal. 

Please find below my candidate details alongside the completed technical assignment deliverables:

---

### 1. Candidate Information

- **Current Location:** [e.g. Dubai, United Arab Emirates / Riyadh, Saudi Arabia / London, UK]
- **Current Package:** [e.g. AED XX,XXX per month / SAR XX,XXX per month / £XX,XXX per annum]
- **Expected Package:** [e.g. AED XX,XXX per month / Negotiable based on role scope and benefits]
- **Notice Period:** [e.g. Immediate / 30 Days]

---

### 2. Technical Assignment Deliverables

- **Live Deployed Chatbot URL:** `https://[your-username]-darglobal-wasalt-ai.hf.space` *(or your Render/cloud URL)*
- **GitHub Repository (Source & Docker):** `https://github.com/[your-github-username]/darglobal-wasalt-ai-chatbot`

---

### 3. Architecture & Implementation Highlights

1. **Data Ingestion & Web Scraping (DarGlobal & Wasalt):**
   - **DarGlobal:** Ingested and structured data from `darglobal.co.uk` for flagship branded residences across Dubai, Spain, Oman, Qatar, and the UK (including *DaVinci Tower by Pagani, Tierra Viva by Automobili Lamborghini in Marbella, Aida by Trump International in Oman, Urban Oasis by Missoni, W Residences Dubai, Les Vagues by Elie Saab*).
   - **Wasalt:** Processed public CDN sitemaps and verified categories from `wasalt.sa` (Saudi PropTech marketplace backed by Dar Al Arkan & Quara), covering key residential communities (*Shams Ar Riyadh, Parisiana Living, Sedra, Al Malqa Penthouses*), as well as Wasalt's official Infath digital real estate auctions.

2. **RAG Retrieval Engine:**
   - Engineered a high-precision hybrid retrieval system utilizing BM25 lexical scoring and entity boosting.
   - Guarantees sub-5ms retrieval of property specifications, prices, locations, currencies, and luxury amenities without hallucination.

3. **OpenRouter Free-Tier LLM Orchestration & Automatic Failover:**
   - Implemented dynamic integration with OpenRouter free-tier models (primary: `meta-llama/llama-3.3-70b-instruct:free`, fallback: `google/gemini-2.0-flash-exp:free`, `qwen/qwen-2.5-72b-instruct:free`).
   - Integrated an automatic model fallback cascade that smoothly recovers if any single free-tier endpoint experiences rate limits (HTTP 429/503), backed by a deterministic context-grounded fallback.
   - Persona crafted specifically as an AI Luxury Real Estate Concierge, fluent in both English and Arabic.

4. **Branded Luxury Interface & Lead Capture:**
   - Designed a full-stack web application with DarGlobal’s signature dark obsidian and champagne gold aesthetic.
   - Features quick-prompt suggestions, a real estate portfolio catalog modal, verified source citation chips, and a VIP private consultation inquiry flow.

5. **Dockerization & Production Deployment:**
   - Packaged inside a lightweight multi-stage `Dockerfile` and `docker-compose.yml`.
   - Deployed directly to the cloud with zero downtime and permanent HTTPS accessibility.

The complete code, documentation, and Docker configuration are available in the attached GitHub repository. I look forward to discussing how my applied AI experience can contribute to DarGlobal’s international digital innovations.

Best regards,

**[Your Full Name]**  
[Your Contact Number / WhatsApp]  
[Your LinkedIn Profile]  
[Your Portfolio / GitHub Profile]

