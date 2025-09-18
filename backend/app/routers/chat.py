
# チャットAPIのルーティング
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Response
from sqlalchemy.orm import Session
from ..schemas import (
    AskRequest, AskResponse, HistoryItem, UpdateMessageRequest, EditRegenResponse
)
from ..services.ai_client import AIClient, AIRateLimitError, AIUpstreamError
from ..db import get_db
from ..repositories import history as repo
from ..config import USE_CONTEXT, MAX_HISTORY, SYSTEM_PROMPT, ENABLE_DB

router = APIRouter()
MAX_LEN = 200

def require_db_enabled():
    if not ENABLE_DB:
        raise HTTPException(status_code=501, detail="database_disabled")

# ユーザーからの質問を受け付け、AI応答を返す
@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest, db: Session = Depends(get_db)):
    sys_prompt = (req.system or SYSTEM_PROMPT or "").strip()
    if len(req.message) > MAX_LEN:
        raise HTTPException(status_code=400, detail="message_too_long")
    if ENABLE_DB:
        u = repo.create_message(db, role="user", text=req.message)
    history_items = []
    if ENABLE_DB and USE_CONTEXT:
        rows = repo.list_messages(db, limit=MAX_HISTORY * 2)
        for r in rows[-MAX_HISTORY:]:
            history_items.append({"role": r.role, "text": r.text})
    client = AIClient()
    try:
        reply, tok_in, tok_out = await client.generate_reply(
            message=req.message, 
            system=sys_prompt if sys_prompt else None, 
            history=history_items
        )
        a = repo.create_message(db, role="assistant", text=reply)
        return AskResponse(reply=reply, tokens_input=tok_in, tokens_output=tok_out)
    except AIRateLimitError as e:
        raise HTTPException(status_code=429, detail="rate_limited") from e
    except AIUpstreamError as e:
        raise HTTPException(status_code=502, detail="upstream_error") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="internal_error") from e

# チャット履歴を取得
@router.get("/history", response_model=list[HistoryItem])
def history(limit: int = Query(20, ge=1, le=200), db: Session = Depends(get_db)):
    if not ENABLE_DB:
        return []
    rows = repo.list_messages(db, limit=limit)
    return [HistoryItem(id=r.id, role=r.role, text=r.text, ts=r.ts) for r in rows]

# ユーザーメッセージの内容を更新
@router.put("/message/{id}", response_model=HistoryItem)
def update_message(
    id: int = Path(..., ge=1),
    body: UpdateMessageRequest = ...,
    db: Session = Depends(get_db),
):
    row = repo.get_message(db, id)
    if not row:
        raise HTTPException(status_code=404, detail="not_found")
    if row.role != "user":
        raise HTTPException(status_code=400, detail="not_editable")
    row = repo.update_message(db, id=id, text=body.text)
    return HistoryItem(id=row.id, role=row.role, text=row.text, ts=row.ts)

# チャット履歴を全削除
@router.delete("/history", status_code=204)
def clear_history(db: Session = Depends(get_db)):
    if not ENABLE_DB:
        raise Response(status_code=204)
    repo.delete_all_messages(db)
    return Response(status_code=204)

# メッセージ編集＆AI応答再生成
@router.post("/message/{id}/edit_regen", response_model=EditRegenResponse)
async def edit_and_regenerate(
    id: int = Path(..., ge=1),
    body: UpdateMessageRequest = ...,
    db: Session = Depends(get_db),
):
    target = repo.get_message(db, id)
    if not target:
        raise HTTPException(status_code=404, detail="not_found")
    if target.role != "user":
        raise HTTPException(status_code=400, detail="not_editable")
    updated = repo.update_message(db, id=id, text=body.text)
    repo.delete_after_id(db, id=id)
    hist_rows = repo.list_messages_upto_id(db, id=id, limit=(MAX_HISTORY * 2 if USE_CONTEXT else None))
    history_items = []
    if USE_CONTEXT:
        for r in hist_rows[-MAX_HISTORY:]:
            history_items.append({"role": r.role, "text": r.text})
    client = AIClient()
    try:
        reply, tok_in, tok_out = await client.generate_reply(
            message=updated.text, system=None, history=history_items
        )
    except AIRateLimitError as e:
        raise HTTPException(status_code=429, detail="rate_limited") from e
    except AIUpstreamError as e:
        raise HTTPException(status_code=502, detail="upstream_error") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="internal_error") from e
    ai = repo.create_message(db, role="assistant", text=reply)
    return EditRegenResponse(
        updated=HistoryItem(id=updated.id, role=updated.role, text=updated.text, ts=updated.ts),
        assistant=HistoryItem(id=ai.id, role=ai.role, text=ai.text, ts=ai.ts),
    )