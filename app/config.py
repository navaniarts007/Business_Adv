import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
# Tried in order if the configured model id is unknown to the API.
FALLBACK_MODELS = ["gemini-flash-latest", "gemini-flash-lite-latest"]
# Sarvam AI: fallback LLM (strong in Indian languages) used when Gemini fails or has no key.
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SARVAM_MODEL = os.getenv("SARVAM_MODEL", "sarvam-105b")
SARVAM_URL = os.getenv("SARVAM_URL", "https://api.sarvam.ai/v2/chat/completions")
COUNTRY =os.getenv("ADVISOR_COUNTRY", "India")
CACHE_HOURS = float(os.getenv("CACHE_HOURS", "6"))

_db = Path(os.getenv("DB_PATH", "data/advisor.db"))
DB_PATH = _db if _db.is_absolute() else BASE_DIR / _db
STATIC_DIR = BASE_DIR / "static"
