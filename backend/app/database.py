"""Database bootstrap. SQLite is intentionally the zero-setup demo default."""

import os
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv("CLAIMFLOW_DATABASE_URL", "sqlite:///./claimflow.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

SCHEMA_VERSION = 1  # Bump when tables change. Demo only: no migrations yet.


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


def check_schema_version(db_engine: Engine) -> None:
    """Stamp a new SQLite DB with SCHEMA_VERSION. Refuse to run on a mismatched one."""
    if db_engine.dialect.name != "sqlite":
        return
    with db_engine.begin() as conn:
        found = conn.execute(text("PRAGMA user_version")).scalar_one()
        if found == 0:
            conn.execute(text(f"PRAGMA user_version = {SCHEMA_VERSION}"))
        elif found != SCHEMA_VERSION:
            path = db_engine.url.database
            raise RuntimeError(
                f"Database schema version {found} differs from code version {SCHEMA_VERSION}. "
                f"Delete the DB file ({path}) and reseed with POST /api/v1/demo/seed."
            )
