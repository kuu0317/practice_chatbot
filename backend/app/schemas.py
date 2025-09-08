from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class AskRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    system: Optional[str] = None

class AskResponse(BaseModel):
    reply: str
    tokens_input: int | None = None
    tokens_output: int | None = None

class HistoryItem(BaseModel):
    id: int
    role: Literal["user","assistant"]
    text: str
    ts: datetime

class UpdateMessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)

class EditRegenResponse(BaseModel):
    updated: HistoryItem
    assistant: HistoryItem