from datetime import datetime, timezone

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Tool(SQLModel, table=True):
    """A company tool people can request access to (GitHub, AWS, Jira...)."""

    __tablename__ = "tool"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, index=True)
    description: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=50)
    # "Deleting" a tool only deactivates it, so old access requests stay valid.
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
