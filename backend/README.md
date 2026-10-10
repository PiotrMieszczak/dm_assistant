# Backend

FastAPI service for DM Assistant. It owns conversations, retrieval, ingestion, and
every model call. The SPA in `frontend/` talks to it over HTTP; streaming uses
[AG-UI](https://docs.ag-ui.com/) over SSE ([ADR-0009](../docs/adr/adr-0009-ag-ui-protocol.md)).

## What runs today

A Research chat turn, with no database and no provider SDK.

- `POST /api/v1/campaigns/{cid}/conversations` — start a conversation (`mode: research`)
- `GET /api/v1/campaigns/{cid}/conversations/{id}/messages` — history
- `POST /api/v1/campaigns/{cid}/conversations/{id}/messages` — send a message; response is
  `text/event-stream` (`RunStarted`, text deltas, `RunFinished`)

The reply comes from `adapters/llm/fake.py`. Conversations live in
`adapters/persistence/memory/`. Auth, Postgres, Claude, Ollama, and retrieval are not
wired yet. The HTTP surface is specified in
[docs/api-contract.md](../docs/api-contract.md).

## Architecture

Hexagonal, as in [docs/folder-structure.md](../docs/folder-structure.md). Dependencies
point inward. The conversation rules do not import FastAPI, a database, or a model SDK.

```
entrypoints  →  application  →  ports  ←  adapters
                     │            │
                     └──── domain ┘
composition.py is the only module that names both sides of a port
```

| Package | Role | Present now |
|---------|------|-------------|
| `app/domain/` | Entities and values. Stdlib only | `assistant/` — `Conversation`, `Message`, `Mode` |
| `app/ports/` | Protocols the use cases depend on | `ConversationRepo`, `LLMProvider`, `Clock` |
| `app/application/` | Use cases. Receives ports, never an adapter | `StartConversation`, `RunAssistantTurn`, `ListMessages` |
| `app/adapters/` | Implementations of ports | In-memory repo, fake LLM, system and frozen clocks |
| `app/entrypoints/http/` | Driving adapter. Routers, Pydantic schemas, SSE, error mapping | Assistant routes |
| `app/composition.py` | Wires ports to adapters and hangs use cases on `app.state` | `build_app()` |
| `app/config.py` | Runtime settings | Empty until providers and Postgres exist |

`import-linter` (contracts in `pyproject.toml`) and `tests/architecture/` fail the build
if a layer imports inward the wrong way, or if a provider SDK is imported outside
`app/adapters/llm/` (BND-002, [ADR-0006](../docs/adr/adr-0006-llm-gateway.md)).

The older layout in [docs/architecture.md](../docs/architecture.md) (`api/`, `models/`,
`gateway/`) is not this tree. Follow `folder-structure.md`.

## Develop

Python 3.11 or newer.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

ruff check app tests
lint-imports
pytest
```

Application tests use the in-memory repository and the fake LLM. They do not need
Postgres or a network.

## Run both apps

From the repository root:

```bash
docker compose up --build
```

| URL | What |
|-----|------|
| http://localhost:8080 | The SPA. nginx proxies `/api`, `/docs`, `/redoc`, and `/openapi.json` to the API, and does not buffer the assistant stream |
| http://localhost:8000/docs | The API and its OpenAPI UI, without the SPA |

`backend/Dockerfile` runs `uvicorn app.composition:build_app --factory`. `frontend/Dockerfile` builds the Vite bundle and serves it with nginx. Conversations are still in memory: a new container starts empty.

## Deployment (later)

Two modes, same code and the same database engine
([ADR-0013](../docs/adr/adr-0013-postgres-for-local-and-hosted.md), PRIN-004). Neither is
a migration of the other. The compose file above does not start PostgreSQL yet — this
process does not open a database connection.

**Local.** PostgreSQL runs beside the API — a container or an installed service
(ADR-0013 IMP-001). There is no SQLite fallback. Uploaded files go to local disk through
the `FileStore` port. Ollama can serve the model with no outbound API.

**Hosted.** The same PostgreSQL, as a managed service or self-hosted on the operator's
hardware. The images in this compose file are that API process and the static bundle.
Uploaded files stay behind `FileStore`: disk or an object store. Which object store is a
deployment note, not an ADR (ADR-0013 IMP-005). Claude is reached through the LLM
Gateway; switching providers is settings, not a redeploy
([ADR-0006](../docs/adr/adr-0006-llm-gateway.md)).

In both modes, schema changes go through versioned migrations. Ingestion runs as a
worker (`entrypoints/worker/`), separate from the request process, so document processing
does not block a session (PRIN-003).
