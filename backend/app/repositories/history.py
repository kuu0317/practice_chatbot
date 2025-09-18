# チャットメッセージの作成・取得・更新・削除を行うリポジトリ

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, delete, asc
from ..models import ChatMessage

def create_message(db: Session, *, role: str, text: str) -> ChatMessage:
    # 新しいチャットメッセージをDBに保存する
    msg = ChatMessage(role=role, text=text)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def update_message(db: Session, *, id: int, text: str) -> Optional[ChatMessage]:
    # 指定IDのチャットメッセージを更新する
    row = db.get(ChatMessage, id)
    if not row:
        return None
    row.text = text
    db.commit()
    db.refresh(row)
    return row

def list_messages(db: Session, *, limit: int = 20) -> List[ChatMessage]:
    # チャットメッセージを新しい順で最大limit件取得し、古い順に並べて返す
    stmt = select(ChatMessage).order_by(desc(ChatMessage.id)).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return list(reversed(rows))

def delete_all_messages(db: Session) -> int:
    # 全てのチャットメッセージを削除し、削除件数を返す
    result = db.execute(delete(ChatMessage))
    db.commit()
    return int(result.rowcount or 0)

def get_message(db: Session, id: int) -> ChatMessage | None:
    # 指定IDのチャットメッセージを取得する
    return db.get(ChatMessage, id)

def delete_after_id(db: Session, *, id: int) -> int:
    # 指定IDより後のチャットメッセージを削除し、削除件数を返す
    result = db.execute(delete(ChatMessage).where(ChatMessage.id > id))
    db.commit()
    return int(result.rowcount or 0)

def list_messages_upto_id(db: Session, *, id: int, limit: int | None = None) -> list[ChatMessage]:
    # 指定ID以下のチャットメッセージを古い順で取得し、limit指定時は末尾N件のみ返す
    if limit:
        stmt = select(ChatMessage).where(ChatMessage.id <= id).order_by(desc(ChatMessage.id)).limit(limit)
        rows = db.execute(stmt).scalars().all()
        return list(reversed(rows))
    else:
        stmt = select(ChatMessage).where(ChatMessage.id <= id).order_by(asc(ChatMessage.id))
        return db.execute(stmt).scalars().all()