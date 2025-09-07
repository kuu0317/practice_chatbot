from fastapi import APIRouter, HTTPException, Depends, Query, Path, Response
from sqlalchemy.orm import Session
from ..schemas import AskRequest, AskResponse, HistoryItem, UpdateMessageRequest
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
    row = repo.update_message(db, id=id, text=body.text)
    if not row:
        raise HTTPException(status_code=404, detail="not_found")
    return HistoryItem(id=row.id, role=row.role, text=row.text, ts=row.ts)

@router.delete("/history", status_code=204)
def clear_history(db: Session = Depends(get_db)):
    """履歴を全消去（グローバル）。認証なしのため開発用途のみ想定。"""
    repo.delete_all_messages(db)
    return Response(status_code=204)