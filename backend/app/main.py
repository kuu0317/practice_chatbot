
# バックエンドAPIサーバーのエントリーポイント
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import chat
from .db import init_db_with_retry

app = FastAPI(title="CB Codecheck (DB+Context)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# サーバー起動時にDB初期化
@app.on_event("startup")
def _startup():
    init_db_with_retry()

app.include_router(chat.router, prefix="/api/chat")

# ヘルスチェック用エンドポイント
@app.get("/health")
def health():
    return {"ok": True}
