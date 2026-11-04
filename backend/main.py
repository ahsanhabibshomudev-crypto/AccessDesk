from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import IS_SQLITE
from app.core.errors import ConflictError, NotFoundError
from app.db.session import create_db_and_tables
from app.routers import tools


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Local SQLite: create the tables automatically. On Supabase (Postgres) the
    # tables come from the Alembic migration instead.
    if IS_SQLITE:
        create_db_and_tables()
    yield


# The docs live under /api because vercel.json only sends /api/* to this backend.
app = FastAPI(
    title="AccessDesk API",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
    lifespan=lifespan,
)

app.include_router(tools.router)


@app.exception_handler(NotFoundError)
async def handle_not_found(_: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
async def handle_conflict(_: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

# dist/ only exists after `npm run build`; in dev the Vite server serves the UI.
if FRONTEND_DIR.is_dir():
    app.frontend("/", directory=FRONTEND_DIR)
