# チャットメッセージの作成・取得・更新・削除を行うリポジトリ

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, delete, asc
from ..model import ChatMessage


# TODO: 新しいチャットメッセージをDBに保存する処理を実装してください。
def create_message(db: Session, *, role: str, text: str) -> 'ChatMessage':
    # --- ガイド ---
    # 1. ChatMessageインスタンスを作成し、db.addで追加します。
    # 2. db.commit(), db.refreshで保存・取得します。
    # 3. 保存したインスタンスを返してください。
    pass  # ←ここに実装


# TODO: 指定IDのチャットメッセージを更新する処理を実装してください。
def update_message(db: Session, *, id: int, text: str) -> Optional['ChatMessage']:
    # --- ガイド ---
    # 1. db.getで該当メッセージを取得します。
    # 2. なければNoneを返します。
    # 3. textを書き換えてdb.commit(), db.refreshで保存します。
    # 4. 更新後のインスタンスを返してください。
    pass  # ←ここに実装


# TODO: チャットメッセージを新しい順で最大limit件取得し、古い順に並べて返す処理を実装してください。
def list_messages(db: Session, *, limit: int = 20) -> list['ChatMessage']:
    # --- ガイド ---
    # 1. select(ChatMessage).order_by(desc(ChatMessage.id)).limit(limit) で取得します。
    # 2. list(reversed(rows)) で古い順に並べ替えます。
    pass  # ←ここに実装


# TODO: 全てのチャットメッセージを削除し、削除件数を返す処理を実装してください。
def delete_all_messages(db: Session) -> int:
    # --- ガイド ---
    # 1. delete(ChatMessage) で全削除します。
    # 2. db.commit() で反映します。
    # 3. 削除件数を返してください。
    pass  # ←ここに実装


# TODO: 指定IDのチャットメッセージを取得する処理を実装してください。
def get_message(db: Session, id: int) -> 'ChatMessage | None':
    # --- ガイド ---
    # 1. db.get(ChatMessage, id) で取得し、そのまま返してください。
    pass  # ←ここに実装


# TODO: 指定IDより後のチャットメッセージを削除し、削除件数を返す処理を実装してください。
def delete_after_id(db: Session, *, id: int) -> int:
    # --- ガイド ---
    # 1. delete(ChatMessage).where(ChatMessage.id > id) で削除します。
    # 2. db.commit() で反映します。
    # 3. 削除件数を返してください。
    pass  # ←ここに実装


# TODO: 指定ID以下のチャットメッセージを古い順で取得し、limit指定時は末尾N件のみ返す処理を実装してください。
def list_messages_upto_id(db: Session, *, id: int, limit: int | None = None) -> list['ChatMessage']:
    # --- ガイド ---
    # 1. where(ChatMessage.id <= id) で絞り込みます。
    # 2. limit指定時はdesc+limit→reversed、未指定時はascで取得します。
    pass  # ←ここに実装