from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Index
from .db import Base

# チャットメッセージのDBモデル定義
# TODO: チャットメッセージ用のモデルクラスを定義してください。
# --- ガイド ---
# 1. Baseを継承したクラス名ChatMessageを作成します。
# 2. __tablename__ = "chat_messages" とします。
# 3. id, role, text, created_at などのカラムを適切な型・制約で定義してください。
# 4. created_atは作成日時(datetime)でデフォルト値を設定します。
# 5. インデックス(Index)も追加してみましょう。
class ChatMessage(Base):
	pass