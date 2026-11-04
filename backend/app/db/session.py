"""Database engine and the session dependency used by the routers."""

from collections.abc import Iterator

from sqlalchemy.pool import NullPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import DATABASE_URL, IS_SQLITE

if IS_SQLITE:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Vercel runs the backend as short-lived serverless functions, so we do not
    # keep a connection pool. `prepare_threshold=None` is needed for Supabase's
    # pooled (transaction mode) connection string.
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,
        connect_args={"prepare_threshold": None},
    )


def create_db_and_tables() -> None:
    """Create tables straight from the models (used for local SQLite only)."""
    import app.models  # noqa: F401  (registers the tables on SQLModel.metadata)

    SQLModel.metadata.create_all(engine)


def get_db() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
