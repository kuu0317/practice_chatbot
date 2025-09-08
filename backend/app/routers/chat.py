from fastapi import APIRouter, HTTPException, Depends, Query, Path, Response
from sqlalchemy.orm import Session
from ..schemas import (
    AskRequest, AskResponse, HistoryItem, UpdateMessageRequest, EditRegenResponse
)
from ..services.ai_client import AIClient, AIRateLimitError, AIUpstreamError
from ..db import get_db
from ..repositories import history as repo
from ..config import USE_CONTEXT, MAX_HISTORY

router = APIRouter()
MAX_LEN = 200

@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest, db: Session = Depends(get_db)):
    if len(req.message) > MAX_LEN:
        raise HTTPException(status_code=400, detail="message_too_long")

    # Create（保存）
    u = repo.create_message(db, role="user", text=req.message)

    # 文脈同送
    history_items = []
    if USE_CONTEXT:
        rows = repo.list_messages(db, limit=MAX_HISTORY * 2)
        for r in rows[-MAX_HISTORY:]:
            history_items.append({"role": r.role, "text": r.text})

    client = AIClient()
    try:
        reply, tok_in, tok_out = await client.generate_reply(
            message=req.message, system=req.system, history=history_items
        )
        # Create（保存）
        a = repo.create_message(db, role="assistant", text=reply)
        return AskResponse(reply=reply, tokens_input=tok_in, tokens_output=tok_out)
    except AIRateLimitError as e:
        raise HTTPException(status_code=429, detail="rate_limited") from e
    except AIUpstreamError as e:
        raise HTTPException(status_code=502, detail="upstream_error") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="internal_error") from e

@router.get("/history", response_model=list[HistoryItem])
def history(limit: int = Query(20, ge=1, le=200), db: Session = Depends(get_db)):
    rows = repo.list_messages(db, limit=limit)
    return [HistoryItem(id=r.id, role=r.role, text=r.text, ts=r.ts) for r in rows]

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
        # ← ここでAI応答の編集を禁止
        raise HTTPException(status_code=400, detail="not_editable")
    row = repo.update_message(db, id=id, text=body.text)
    return HistoryItem(id=row.id, role=row.role, text=row.text, ts=row.ts)

@router.delete("/history", status_code=204)
def clear_history(db: Session = Depends(get_db)):
    """履歴を全消去（グローバル）。認証なしのため開発用途のみ想定。"""
    repo.delete_all_messages(db)
    return Response(status_code=204)

@router.post("/message/{id}/edit_regen", response_model=EditRegenResponse)
async def edit_and_regenerate(
    id: int = Path(..., ge=1),
    body: UpdateMessageRequest = ...,
    db: Session = Depends(get_db),
):
    # 1) 対象メッセージを取得 & バリデーション（ユーザー発話のみ）
    target = repo.get_message(db, id)
    if not target:
        raise HTTPException(status_code=404, detail="not_found")
    if target.role != "user":
        raise HTTPException(status_code=400, detail="not_editable")

    # 2) 対象を更新（本文を上書き）
    updated = repo.update_message(db, id=id, text=body.text)

    # 3) 後続メッセージを全削除（idより大きいものを全て）
    repo.delete_after_id(db, id=id)

    # 4) 文脈（id以下）を取得し、必要なら末尾MAX_HISTORY件に絞る
    hist_rows = repo.list_messages_upto_id(db, id=id, limit=(MAX_HISTORY * 2 if USE_CONTEXT else None))
    history_items = []
    if USE_CONTEXT:
        for r in hist_rows[-MAX_HISTORY:]:
            history_items.append({"role": r.role, "text": r.text})

    # 5) 再生成
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

    # 6) 新しいAI応答を保存
    ai = repo.create_message(db, role="assistant", text=reply)

    # 7) 結果を返す（フロントは受け取らずに再取得でもOK）
    return EditRegenResponse(
        updated=HistoryItem(id=updated.id, role=updated.role, text=updated.text, ts=updated.ts),
        assistant=HistoryItem(id=ai.id, role=ai.role, text=ai.text, ts=ai.ts),
    )