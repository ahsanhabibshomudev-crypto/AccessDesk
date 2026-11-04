"""Request and response shapes for the tools API (validation lives here)."""

from datetime import datetime, timezone

from pydantic import field_validator, model_validator
from sqlmodel import Field, SQLModel


def _strip(value: object) -> object:
    return value.strip() if isinstance(value, str) else value


def _blank_to_none(value: object) -> object:
    value = _strip(value)
    return None if value == "" else value


class ToolCreate(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=50)

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, value: object) -> object:
        return _strip(value)

    @field_validator("description", "category", mode="before")
    @classmethod
    def clean_optional(cls, value: object) -> object:
        return _blank_to_none(value)


class ToolUpdate(SQLModel):
    """Every field is optional: only the fields you send are changed (PATCH)."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, value: object) -> object:
        return _strip(value)

    @field_validator("description", "category", mode="before")
    @classmethod
    def clean_optional(cls, value: object) -> object:
        return _blank_to_none(value)

    @model_validator(mode="after")
    def required_fields_not_null(self) -> "ToolUpdate":
        for field in ("name", "is_active"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class ToolRead(SQLModel):
    id: int
    name: str
    description: str | None
    category: str | None
    is_active: bool
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def assume_utc(cls, value: datetime) -> datetime:
        # SQLite hands back naive datetimes. We always store UTC, so say so,
        # otherwise the browser would read the time as local time.
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


class ToolList(SQLModel):
    items: list[ToolRead]
    total: int
    skip: int
    limit: int
