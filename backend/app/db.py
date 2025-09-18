import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import DATABASE_URL

# SQLAlchemyのベースクラス定義
class Base(DeclarativeBase):
    pass

# DBエンジン生成
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    future=True,
)

# セッションファクトリ生成
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# DBセッションを取得するジェネレータ
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DB初期化（リトライ付き）
def init_db_with_retry(retries: int = 20, wait: float = 0.5):
    for i in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                break
        except Exception:
            time.sleep(wait)
    from . import models  # noqa
    Base.metadata.create_all(bind=engine)