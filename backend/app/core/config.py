"""Settings read from environment variables (or a local backend/.env file)."""

import os

from dotenv import load_dotenv

load_dotenv()

# Local development uses a SQLite file. In production set DATABASE_URL to the
# Supabase connection string, nothing else in the code has to change.
DEFAULT_DATABASE_URL = "sqlite:///./accessdesk.db"


def normalise_database_url(url: str) -> str:
    """Supabase gives `postgresql://...`; SQLAlchemy needs the driver name too."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


DATABASE_URL = normalise_database_url(os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL)
IS_SQLITE = DATABASE_URL.startswith("sqlite")
