from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Index
from .db import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String(16))         # "user" | "assistant"
    text: Mapped[str] = mapped_column(String(4000))
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

Index("ix_chat_messages_ts_desc", ChatMessage.ts.desc())