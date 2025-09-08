from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Index
from .db import Base

# チャットメッセージのDBモデル定義
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # メッセージID
    role: Mapped[str] = mapped_column(String(16))  # 発言者の役割（user/assistant）
    text: Mapped[str] = mapped_column(String(4000))  # メッセージ本文
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # 作成日時

# タイムスタンプ降順インデックス
Index("ix_chat_messages_ts_desc", ChatMessage.ts.desc())