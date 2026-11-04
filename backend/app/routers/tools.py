"""REST endpoints for tools: Create, Read list, Read single, Update, Delete."""

from fastapi import APIRouter, Query, Response, status

from app.deps import SessionDep
from app.schemas import ToolCreate, ToolList, ToolRead, ToolUpdate
from app.services import tool_service

router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.post("", response_model=ToolRead, status_code=status.HTTP_201_CREATED)
def create_tool(data: ToolCreate, session: SessionDep):
    return tool_service.create_tool(session, data)


@router.get("", response_model=ToolList)
def list_tools(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    include_inactive: bool = False,
):
    items, total = tool_service.list_tools(session, skip, limit, include_inactive)
    return ToolList(items=items, total=total, skip=skip, limit=limit)


@router.get("/{tool_id}", response_model=ToolRead)
def get_tool(tool_id: int, session: SessionDep):
    return tool_service.get_tool(session, tool_id)


@router.patch("/{tool_id}", response_model=ToolRead)
def update_tool(tool_id: int, data: ToolUpdate, session: SessionDep):
    return tool_service.update_tool(session, tool_id, data)


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tool(tool_id: int, session: SessionDep):
    tool_service.deactivate_tool(session, tool_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
