from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, delete, asc
from ..models import ChatMessage

def create_message(db: Session, *, role: str, text: str) -> ChatMessage:
    msg = ChatMessage(role=role, text=text)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def update_message(db: Session, *, id: int, text: str) -> Optional[ChatMessage]:
    row = db.get(ChatMessage, id)
    if not row:
        return None
    row.text = text
    db.commit()
    db.refresh(row)
    return row

def list_messages(db: Session, *, limit: int = 20) -> List[ChatMessage]:
    stmt = select(ChatMessage).order_by(desc(ChatMessage.id)).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return list(reversed(rows))  # 古→新

def delete_all_messages(db: Session) -> int:
    """全メッセージを削除して件数を返す（グローバルリセット）"""
    result = db.execute(delete(ChatMessage))
    db.commit()
    # SQLAlchemy 2.x: rowcount が入る（方言により None になり得るので int 化）
    return int(result.rowcount or 0)

def get_message(db: Session, id: int) -> ChatMessage | None:
    return db.get(ChatMessage, id)

def delete_after_id(db: Session, *, id: int) -> int:
    """指定idより後の全メッセージを削除。削除件数を返す。"""
    result = db.execute(delete(ChatMessage).where(ChatMessage.id > id))
    db.commit()
    return int(result.rowcount or 0)

def list_messages_upto_id(db: Session, *, id: int, limit: int | None = None) -> list[ChatMessage]:
    """id以下のメッセージを昇順（古→新）で返す。limit指定時は末尾N件のみ。"""
    if limit:
        stmt = select(ChatMessage).where(ChatMessage.id <= id).order_by(desc(ChatMessage.id)).limit(limit)
        rows = db.execute(stmt).scalars().all()
        return list(reversed(rows))
    else:
        stmt = select(ChatMessage).where(ChatMessage.id <= id).order_by(asc(ChatMessage.id))
        return db.execute(stmt).scalars().all()