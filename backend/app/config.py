import os

# 環境変数から設定値を取得
def _bool(v: str | None) -> bool:
    return str(v or "").lower() in ("1","true","yes","on")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://chat:chatpass@db:5432/chat")

OPENAI_DRYRUN = os.getenv("OPENAI_DRYRUN", "0") == "1"
ENABLE_DB = _bool(os.getenv("ENABLE_DB", "true"))

USE_CONTEXT = _bool(os.getenv("USE_CONTEXT", "true"))
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "10") or 10)