# AccessDesk

A web portal where employees request access to company tools (GitHub, AWS, Jira...), managers approve or reject, and admins manage the tools and review an audit log.

**Live app:** add your Vercel URL here after deploying.

## Release status

| Release | What it contains | Status |
|---|---|---|
| **MVP** (mid-term demo) | Tool catalog: create, read list, read single, update and delete, with an audit entry for every change | Done |
| **Beta** (final demo) | Login with JWT, roles (Employee, Manager, Admin), security scopes, access requests, profile dashboard, audit log viewer | Planned |

Full details: [PRD](docs/01-prd.md), [SRS](docs/02-srs.md), [TDD](docs/03-tdd.md).

## Tech stack

- **Frontend:** React 19 + TypeScript, built with Vite
- **Backend:** FastAPI (Python), SQLModel for the database models, Alembic for migrations
- **Database:** SQLite locally, Supabase (PostgreSQL) in production
- **Hosting:** Vercel (frontend and backend in one project, see `vercel.json`)

## Run it locally

You need Python 3.10+ and Node.js 22+. On macOS/Linux use `python3` instead of `python`.

**Backend** (terminal 1):

```
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1      # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
fastapi dev main.py
```

The API runs on <http://localhost:8000> and its interactive docs are at <http://localhost:8000/api/docs>. The SQLite database file (`backend/accessdesk.db`) and its tables are created automatically on the first start.

**Frontend** (terminal 2):

```
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite forwards `/api` requests to the backend on port 8000.

**Tests** (backend, with the virtual environment active):

```
cd backend
pytest
```

## API (MVP)

All endpoints are under `/api`. Errors are JSON like `{"detail": "..."}`.

| Operation | Method and path | Success | Errors |
|---|---|---|---|
| Create | `POST /api/tools` | 201 + the tool | 409 name already exists, 422 invalid input |
| Read list | `GET /api/tools?skip=0&limit=20&include_inactive=false` | 200 `{items, total, skip, limit}` | 422 bad paging values |
| Read single | `GET /api/tools/{id}` | 200 + the tool | 404 not found |
| Update | `PATCH /api/tools/{id}` | 200 + the tool | 404, 409, 422 |
| Delete | `DELETE /api/tools/{id}` | 204 | 404 |

A tool has `id`, `name` (unique, ignoring upper/lower case), `description`, `category`, `is_active` and `created_at`.

**Delete only deactivates a tool** (`is_active = false`) so access requests that point at it stay valid later. Deleted tools are hidden from the list unless `include_inactive=true`, and can be restored with `PATCH {"is_active": true}`.

Every create, update and delete also writes a row to the `audit_log` table in the same database transaction.

## Database and environment variables

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Where the data lives. Empty = local SQLite file. Set it to the Supabase connection string for production. |

For local use, copy `backend/.env.example` to `backend/.env`. Never commit `.env`.

### Migrations

On SQLite the tables are created automatically. On Supabase the tables come from the Alembic migrations in `backend/alembic/versions`. Run them from your own computer, not inside Vercel:

```
cd backend
# Windows PowerShell:
$env:DATABASE_URL = "postgresql://..."
# macOS/Linux:  export DATABASE_URL="postgresql://..."
alembic upgrade head
```

After you change a model, create a new migration with `alembic revision --autogenerate -m "describe the change"`, read the generated file, then run `alembic upgrade head`.

## Deploy to Vercel with Supabase

1. In Supabase, create a project and copy its **connection string** (Connect button, pooled connection). Replace the password placeholder with your database password and URL-encode special characters.
2. Run the migration against Supabase from your computer (see above).
3. In Vercel, open the project, go to **Settings > Environment Variables**, and add `DATABASE_URL` with that connection string. Redeploy.
4. Push to `main`. Vercel builds and deploys automatically.
5. Check `https://<your-app>.vercel.app/api/health` and `/api/docs`.

The backend does not keep a connection pool, because each Vercel request can run in a new short-lived function.

## Project structure

```
backend/
  main.py              FastAPI app, error handlers, router setup
  app/
    core/              settings (config.py) and business errors
    db/                database engine and session
    models/            database tables (Tool, AuditLog)
    schemas/           request and response shapes with validation
    routers/           HTTP endpoints
    services/          business rules (duplicate names, audit entries)
  alembic/             database migrations
  tests/               API tests
frontend/src/
  api/                 functions that call the backend
  types/               TypeScript types for the API data
  components/          ToolList, ToolDetail, ToolForm
  App.tsx              page layout
```

## Working on the project

- Every task starts as a GitHub Issue.
- Work happens on a feature branch named `yourname/#<issue>-short-description`.
- Commit messages look like `feat: add tool endpoints (#4)`.
- A Pull Request describes the change (Summary, Changes, Notes, Verification). The last PR for an issue says `Closes #<issue>`.
- Every PR is merged into `main`.

## Troubleshooting

- **`fastapi` not found:** activate the virtual environment first.
- **`Request failed: 500` in the app:** the backend is not running.
- **Port 8000 or 5173 already in use:** stop the other program, or pick another port.
- **Deployed API returns 500:** check that `DATABASE_URL` is set in Vercel and that `alembic upgrade head` was run against Supabase.
- **`relation "tool" does not exist`:** the migration has not been run on that database.
