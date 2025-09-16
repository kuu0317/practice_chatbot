import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import DATABASE_URL


# SQLAlchemyのベースクラス定義
# TODO: DeclarativeBaseを継承したBaseクラスを定義してください。
# --- ガイド ---
# 1. DeclarativeBaseを継承したBaseクラスを作成します。
#
class Base(DeclarativeBase):
    pass

# TODO: SQLAlchemyのDB初期化処理を実装してください。
# --- ガイド ---
# 1. create_engineでDBエンジンを作成します。
# 2. sessionmakerでSessionLocalを作成します。
# 3. Base.metadata.create_allでテーブルを作成します。
#
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# DBセッションを取得するジェネレータ
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DB初期化（リトライ付き）
# TODO: DBのテーブルを作成する処理を実装してください。
def init_db_with_retry(retries: int = 20, wait: float = 0.5):
    # --- ガイド ---
    # 1. engine.connect() でDB接続できるまでリトライします。
    # 2. models.pyをimportし、Base.metadata.create_all(bind=engine)でテーブルを作成します。
    # 3. 例外処理・リトライも忘れずに。
    pass  # TODO: DB初期化処理を実装してください