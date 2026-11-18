# ==============================================================
# DarGlobal & Wasalt AI Real Estate Concierge Dockerfile
# Optimized for local Docker, Hugging Face Spaces, Render, & Koyeb
# ==============================================================

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

WORKDIR /app

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and datasets
COPY . .

# Ensure data and knowledge base are ready
RUN python scrapers/build_knowledge_base.py

# Expose port (7860 is default for Hugging Face Spaces & easily mapped to 80/8000)
EXPOSE 7860

# Run FastAPI app
CMD ["python", "app.py"]
