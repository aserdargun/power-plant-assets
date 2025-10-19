from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _get_database_url() -> str:
    """Return the application database URL."""
    return os.getenv("DATABASE_URL", "sqlite:///./app.db")


# SQLite needs check_same_thread disabled for multi-threaded FastAPI usage.
def _engine_options(url: str) -> dict[str, object]:
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


DATABASE_URL = _get_database_url()
engine = create_engine(DATABASE_URL, **_engine_options(DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope(session: Optional[Session] = None) -> Generator[Session, None, None]:
    """
    Provide a transactional scope around a series of operations.

    Primarily useful in scripts or background jobs.
    """
    managed_session = session or SessionLocal()
    try:
        yield managed_session
        managed_session.commit()
    except Exception:
        managed_session.rollback()
        raise
    finally:
        if session is None:
            managed_session.close()
