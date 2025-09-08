from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# チャットAPIのリクエストスキーマ
class AskRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    system: Optional[str] = None

# チャットAPIのレスポンススキーマ
class AskResponse(BaseModel):
    reply: str
    tokens_input: int | None = None
    tokens_output: int | None = None

# チャット履歴アイテムのスキーマ
class HistoryItem(BaseModel):
    id: int
    role: Literal["user","assistant"]
    text: str
    ts: datetime

# メッセージ更新リクエストのスキーマ
class UpdateMessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)

# 編集・再生成APIのレスポンススキーマ
class EditRegenResponse(BaseModel):
    updated: HistoryItem
    assistant: HistoryItem