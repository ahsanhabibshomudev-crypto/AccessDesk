import os

# Must be set before the app is imported, so tests never touch a real database.
os.environ["DATABASE_URL"] = "sqlite://"

from collections.abc import Iterator  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

import app.models  # noqa: E402,F401  (registers the tables)
from app.db.session import get_db  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture()
def engine():
    # One shared in-memory database per test, thrown away afterwards.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture()
def session(engine) -> Iterator[Session]:
    with Session(engine) as db:
        yield db


@pytest.fixture()
def client(engine) -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    # Not used as a context manager on purpose: that would run the lifespan.
    yield TestClient(app)
    app.dependency_overrides.clear()
