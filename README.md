# taskboard

A FastAPI to-do / task board app I'm building to learn **FastAPI, AWS, and AI integration** hands-on.

This is a learning project, not a product. The point is to build each layer myself,
one step at a time, and understand why each piece is there before moving on.

## Roadmap

Each step builds on the previous one. I move to the next only once the current one works
and I understand it.

1. **CRUD** — FastAPI to-do app with Postgres. Create, list, update, delete tasks.
2. **Auth** — User signup/login with JWT. Protect the task endpoints.
   Add OAuth (Google login) only if it still feels interesting afterwards.
3. **Email + queue** — Send a welcome/reminder email through a background worker
   (Celery or arq + Redis) instead of inline in the request.
4. **Docker** — Dockerfile for the app, docker-compose for app + Postgres + Redis + worker.
5. **AWS deploy** — Push the image to ECR, run it on ECS, RDS for Postgres, swap Redis for SQS.
   Start studying for the AWS Developer Associate cert alongside this step.
6. **AI feature** — One thing, e.g. paste text and Claude extracts tasks with structured output.
   Then go deeper into prompting, tool use, and evals.

### Where I am now

Step 1, in progress. Postgres, Alembic migrations, and the `Board` / `Task` models exist.
CRUD endpoints are done for both:

- **Boards** — `POST /boards`, `GET /boards`, `GET/PATCH/DELETE /boards/{id}`
- **Tasks** — shallow nesting: `POST/GET /boards/{board_id}/tasks` to create and list,
  `GET/PATCH/DELETE /tasks/{id}` for a single task. PATCH can move a task to another board.

Deleting a board also deletes its tasks (`ON DELETE CASCADE` on `task.board_id`).
Tests are next (pytest + `TestClient`), then step 2.

Docker (step 4) came early because it was the easiest way to run Postgres locally.
It gets revisited properly when Redis and the worker land.

## Stack

| Piece | Choice |
| --- | --- |
| Language | Python 3.14 |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Web framework | FastAPI |
| ORM / models | SQLModel (SQLAlchemy + Pydantic) |
| Database | Postgres 18 (`pgvector/pgvector:pg18`, so embeddings are possible later) |
| Driver | psycopg 3 |
| Migrations | Alembic |
| Local dev | Docker Compose |

## Running it

Everything runs inside Docker — the `DATABASE_URL` and the `db` hostname only exist
inside the Compose network.

```bash
docker compose up --build
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Postgres: `localhost:5432` (`postgres` / `postgres`, database `taskboard`)

The project folder is bind-mounted into the container, so edits hot-reload.

### Migrations

Shortcuts live in the [Makefile](Makefile) and run through `docker compose exec api`.

```bash
# Generate a migration by diffing the models against the live database
make revision m="add user table"

# Apply everything that hasn't run yet
make migrate
```

Always read a generated migration before applying it — autogenerate guesses, especially
around enums, renames, and server defaults.

Constraint and index names come from the naming convention in
[app/models/\_\_init\_\_.py](app/models/__init__.py). Without it, Postgres picks the names and
any migration that drops or changes a constraint fails with "constraint name is None".

## Layout

```
app/
  main.py              # FastAPI app; registers each module's router
  db.py                # engine + per-request session dependency (SessionDep)
  modules/             # one folder per feature, like NestJS modules
    boards/
      router.py        # routes (the "controller") - HTTP concerns, 404s
      service.py       # database work, takes the session as an argument
      schemas.py       # request/response shapes (BoardCreate, BoardUpdate, BoardPublic)
    tasks/             # same structure; routes span /boards/{id}/tasks and /tasks/{id}
      router.py
      service.py
      schemas.py       # TaskCreate, TaskUpdate, TaskPublic
  models/
    __init__.py        # constraint naming convention + imports every model for Alembic
    board.py           # Board table
    task.py            # Task table + Status enum
  alembic/
    env.py             # reads DATABASE_URL from the environment
    versions/          # migration history
compose.yaml           # api + db services
Dockerfile             # python:3.14-slim + uv
Makefile               # alembic shortcuts
AGENTS.md              # how AI agents should behave in this repo
```

## A note on the comments

The code is commented more heavily than production code would be. That's deliberate —
the comments are my notes on *why* something is the way it is, written for me to re-read
later. They are part of the learning, not clutter to be cleaned up.
