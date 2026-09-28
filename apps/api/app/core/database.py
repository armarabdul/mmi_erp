from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger

db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
pool_kwargs = {}

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    pool_kwargs = {
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_pre_ping": True,
    }

engine = create_engine(
    db_url,
    echo=settings.DB_ECHO,
    connect_args=connect_args,
    **pool_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_readonly_db() -> Generator[Session, None, None]:
    """Provides a session designated for read-only analytical queries."""
    db = SessionLocal()
    try:
        if db_url.startswith("postgresql"):
            from sqlalchemy import text
            db.execute(text("SET TRANSACTION READ ONLY"))
        yield db
    finally:
        db.rollback()
        db.close()
