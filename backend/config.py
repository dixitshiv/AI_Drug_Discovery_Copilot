import os
from dotenv import load_dotenv

load_dotenv(override=True)

# ── PubMed / Entrez ──────────────────────────────────────────────────────────
ENTREZ_EMAIL = os.getenv("ENTREZ_EMAIL", "your_email@example.com")
ENTREZ_API_KEY = os.getenv("ENTREZ_API_KEY", "")   # optional but raises rate limits

# ── Ollama (local LLM) ────────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")    # any model pulled in Ollama

# ── Literature Agent settings ─────────────────────────────────────────────────
MAX_PAPERS = int(os.getenv("MAX_PAPERS", "20"))          # papers fetched per query
MAX_GENES = int(os.getenv("MAX_GENES", "10"))            # top‑N genes to return
