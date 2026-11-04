from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel

from app.models.tool import utcnow


class AuditLog(SQLModel, table=True):
    """One row per important action. Rows are only ever inserted."""

    __tablename__ = "audit_log"

    id: int | None = Field(default=None, primary_key=True)
    # Empty until Beta, when login tells us who the actor is.
    actor_id: int | None = Field(default=None)
    action: str = Field(max_length=50)
    entity_type: str = Field(max_length=50)
    entity_id: int
    details: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
