import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
ALGORITHM = "HS256"

_base = Path(__file__).parent.parent.parent
FRONTEND_DIR = _base / "frontend"
DB_PATH = os.getenv("DB_PATH", str(_base / "just_wright.db"))

MODEL_CLAUDE = "claude-opus-4-8"
GEMINI_MODELS = [m.strip() for m in os.getenv(
    "GEMINI_MODELS", "gemini-flash-latest,gemini-3.6-flash,gemini-flash-lite-latest"
).split(",") if m.strip()]
GEMINI_TIMEOUT = int(os.getenv("GEMINI_TIMEOUT", "20"))

FREE_DAILY_LIMIT = int(os.getenv("FREE_DAILY_LIMIT", "50"))
AUTH_DAILY_LIMIT = int(os.getenv("AUTH_DAILY_LIMIT", "200"))


def _resolve_provider() -> str:
    if AI_PROVIDER == "claude":
        return "claude" if ANTHROPIC_API_KEY else "none"
    if AI_PROVIDER == "gemini":
        return "gemini" if GEMINI_API_KEY else "none"
    if AI_PROVIDER == "auto":
        if GEMINI_API_KEY:
            return "gemini"
        if ANTHROPIC_API_KEY:
            return "claude"
    return "none"


ACTIVE_PROVIDER = _resolve_provider()
AI_ENABLED = ACTIVE_PROVIDER != "none"
