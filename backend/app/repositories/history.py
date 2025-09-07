from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
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