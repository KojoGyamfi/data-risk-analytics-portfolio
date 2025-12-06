from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .config import DATABASE_URL

# SQLAlchemy engine and session factory
engine = create_engine(
    DATABASE_URL,
    future=True,
    echo=False,  # set True during debugging to see SQL
)

SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
)
