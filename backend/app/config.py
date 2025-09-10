import os

# 環境変数から設定値を取得
def _bool(v: str | None) -> bool:
    return str(v or "").lower() in ("1","true","yes","on")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://chat:chatpass@db:5432/chat")

ENABLE_DB = _bool(os.getenv("ENABLE_DB", "true"))
OPENAI_DRYRUN = _bool(os.getenv("OPENAI_DRYRUN", "1"))

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "").strip()
MAX_TOKENS_OUTPUT = int(os.getenv("MAX_TOKENS_OUTPUT", "256") or 256)

USE_CONTEXT = _bool(os.getenv("USE_CONTEXT", "true"))
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "10") or 10)