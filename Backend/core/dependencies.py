"""Shared dependencies and utilities."""
from typing import Generator
from sqlalchemy.orm import Session
from core.database import get_db


def get_database_session() -> Generator[Session, None, None]:
    """Get database session dependency."""
    yield from get_db()
