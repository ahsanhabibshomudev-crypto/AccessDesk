"""Business rules for tools. The router only handles HTTP, this file does the work."""

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from app.core.errors import ConflictError, NotFoundError
from app.models import Tool
from app.schemas import ToolCreate, ToolUpdate
from app.services import audit_service

NAME_TAKEN = "A tool with this name already exists"


def _ensure_name_free(session: Session, name: str, ignore_id: int | None = None) -> None:
    """Tool names are unique, ignoring upper/lower case."""
    query = select(Tool.id).where(func.lower(Tool.name) == name.lower())
    if ignore_id is not None:
        query = query.where(Tool.id != ignore_id)
    if session.exec(query).first() is not None:
        raise ConflictError(NAME_TAKEN)


def _commit(session: Session) -> None:
    try:
        session.commit()
    except IntegrityError:  # two people saved the same name at the same moment
        session.rollback()
        raise ConflictError(NAME_TAKEN) from None


def get_tool(session: Session, tool_id: int) -> Tool:
    tool = session.get(Tool, tool_id)
    if tool is None:
        raise NotFoundError("Tool not found")
    return tool


def list_tools(
    session: Session, skip: int, limit: int, include_inactive: bool
) -> tuple[list[Tool], int]:
    query = select(Tool)
    count_query = select(func.count()).select_from(Tool)
    if not include_inactive:
        query = query.where(col(Tool.is_active).is_(True))
        count_query = count_query.where(col(Tool.is_active).is_(True))

    total = session.exec(count_query).one()
    items = session.exec(
        query.order_by(col(Tool.created_at).desc(), col(Tool.id).desc())
        .offset(skip)
        .limit(limit)
    ).all()
    return list(items), total


def create_tool(session: Session, data: ToolCreate) -> Tool:
    _ensure_name_free(session, data.name)
    tool = Tool.model_validate(data)
    session.add(tool)
    try:
        session.flush()  # sends the INSERT so the new id exists for the audit row
    except IntegrityError:
        session.rollback()
        raise ConflictError(NAME_TAKEN) from None
    assert tool.id is not None
    audit_service.record(session, "tool.create", tool.id, f"Created tool '{tool.name}'")
    _commit(session)
    session.refresh(tool)
    return tool


def update_tool(session: Session, tool_id: int, data: ToolUpdate) -> Tool:
    tool = get_tool(session, tool_id)
    changes = data.model_dump(exclude_unset=True)  # only what the client sent
    if not changes:
        return tool
    if "name" in changes:
        _ensure_name_free(session, changes["name"], ignore_id=tool.id)

    tool.sqlmodel_update(changes)
    session.add(tool)
    audit_service.record(
        session, "tool.update", tool_id, "Changed: " + ", ".join(sorted(changes))
    )
    _commit(session)
    session.refresh(tool)
    return tool


def deactivate_tool(session: Session, tool_id: int) -> None:
    """DELETE does not remove the row. It hides the tool, so old requests still point at it."""
    tool = get_tool(session, tool_id)
    if tool.is_active:
        tool.is_active = False
        session.add(tool)
        audit_service.record(session, "tool.deactivate", tool_id, f"Deactivated tool '{tool.name}'")
        _commit(session)
