from sqlmodel import Session

from app.models import AuditLog


def record(
    session: Session,
    action: str,
    entity_id: int,
    details: str | None = None,
    entity_type: str = "tool",
    actor_id: int | None = None,
) -> None:
    """Add an audit row to the current transaction (the caller commits).

    Because it is committed together with the change itself, an action and its
    audit entry either both exist or neither does.
    """
    session.add(
        AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
        )
    )
