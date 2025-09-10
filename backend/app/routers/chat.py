
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
    # TODO: ユーザーのメッセージをDBに保存する処理を実装してください。
    # --- ガイド ---
    # 1. repo.create_message(db, role="user", text=req.message) で保存します。
    # 2. 保存した内容は後続の履歴参照にも使えます。
    # 3. DB無効時はスキップしてください。
    if ENABLE_DB:
        pass  # ←ここに実装
    history_items = []
    # TODO: チャット履歴をDBから取得し、history_itemsリストに格納してください。
    # --- ガイド ---
    # 1. repo.list_messages(db, limit=MAX_HISTORY * 2) で履歴を取得します。
    # 2. 末尾MAX_HISTORY件だけをhistory_itemsに追加します。
    # 3. DB無効時は空リストのままでOKです。
    if ENABLE_DB and USE_CONTEXT:
        pass  # ←ここに実装
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
    # TODO: チャット履歴をDBから取得し、HistoryItemのリストとして返してください。
    # --- ガイド ---
    # 1. repo.list_messages(db, limit=limit) で履歴を取得します。
    # 2. 各行をHistoryItem（例: HistoryItem(id=r.id, role=r.role, text=r.text, ts=r.ts)）に変換して返します。
    # 返却値の型は list[HistoryItem] です。
    # 例:
    #   rows = repo.list_messages(db, limit=limit)
    #   return [HistoryItem(id=r.id, role=r.role, text=r.text, ts=r.ts) for r in rows]
    pass  # ←ここに実装

# ユーザーメッセージの内容を更新
@router.put("/message/{id}", response_model=HistoryItem)
def update_message(
    id: int = Path(..., ge=1),
    body: UpdateMessageRequest = ...,
    db: Session = Depends(get_db),
):
    # TODO: 指定IDのメッセージを取得・更新し、HistoryItemとして返してください。
    # --- ガイド ---
    # 1. repo.get_message(db, id) で取得し、なければ404を返します。
    #    例: if not row: raise HTTPException(status_code=404, detail="not_found")
    # 2. roleがuser以外なら400を返します。
    #    例: if row.role != "user": raise HTTPException(status_code=400, detail="not_editable")
    # 3. repo.update_message(db, id=id, text=body.text) で更新します。
    # 4. 更新後の内容をHistoryItemにして返します。
    #    例: return HistoryItem(id=row.id, role=row.role, text=row.text, ts=row.ts)
    pass  # ←ここに実装

# チャット履歴を全削除
@router.delete("/history", status_code=204)
def clear_history(db: Session = Depends(get_db)):
    if not ENABLE_DB:
        raise Response(status_code=204)
    # TODO: チャット履歴を全削除する処理を実装してください。
    # --- ガイド ---
    # 1. repo.delete_all_messages(db) で全削除します。
    # 2. 削除後は204を返します。
    if not ENABLE_DB:
        return Response(status_code=204)
    pass  # ←ここに実装

# メッセージ編集＆AI応答再生成
@router.post("/message/{id}/edit_regen", response_model=EditRegenResponse)
async def edit_and_regenerate(
    id: int = Path(..., ge=1),
    body: UpdateMessageRequest = ...,
    db: Session = Depends(get_db),
):
    # TODO: メッセージ編集・AI応答再生成の一連の処理を実装してください。
    # --- ガイド ---
    # 1. repo.get_message(db, id) で対象を取得し、なければ404。
    # 2. roleがuser以外なら400。
    # 3. repo.update_message(db, id=id, text=body.text) で本文を更新。
    # 4. repo.delete_after_id(db, id=id) で後続メッセージを削除。
    # 5. repo.list_messages_upto_id(db, id=id, limit=...) で文脈を取得。
    # 6. 必要ならhistory_itemsに詰める。
    # 7. AIClientで再生成し、repo.create_messageで保存。
    # 8. EditRegenResponseで返却。
    pass  # ←ここに実装