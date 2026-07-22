import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Sử dụng SQLite cho local/test và PostgreSQL cho production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quick_quote.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency helper lấy SQLAlchemy DB Session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Khởi tạo bảng cơ sở dữ liệu."""
    Base.metadata.create_all(bind=engine)
