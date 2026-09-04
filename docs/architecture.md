# Architecture

The same diagrams are on a Miro board — **[open the architecture board](https://miro.com/app/board/uXjVHrcVIJQ=/)** — which is
easier to walk someone through than a page of Mermaid. This file stays the source of
truth; the board mirrors it.

## Shape

```mermaid
flowchart TB
    subgraph FE["Frontend — React 19 + Vite + TypeScript"]
        UI["Screens (CSS Modules + design tokens)"]
        RQ["TanStack Query — server state"]
        ZS["Zustand — UI state"]
        SSE["EventSource — streaming"]
    end

    subgraph BE["Backend — FastAPI"]
        API["REST endpoints"]
        ING["Ingestion worker"]
        RET["Retrieval"]
        GW["LLM Gateway"]
    end

    subgraph EXT["Providers"]
        OL["Ollama (local)"]
        CL["Claude API"]
    end

    subgraph DATA["Storage"]
        DB[("SQLite + FTS5")]
        FS[("Uploaded files")]
    end

    UI --> RQ --> API
    UI --> ZS
    SSE -.->|"token stream"| API

    API --> DB
    API --> ING
    ING -->|"extract → chunk → index"| DB
    ING --> FS

    API --> RET --> DB
    RET -->|"grounding context"| GW
    GW --> OL
    GW --> CL

    style ING fill:#7FD4A0,color:#0A0C0F
    style GW fill:#E8B87A,color:#0A0C0F
```

The green path is deterministic and never calls a model. The amber path is the only
place a model is invoked.

## Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Frontend framework | React 19 + TypeScript (strict) | [ADR-0001](adr/adr-0001-react-vite-spa.md) |
| Build / dev server | Vite | Same ADR — SPA with no SSR need |
| Routing | React Router v7 | Client routing matches the design's screen model |
| Server state | TanStack Query | Caching, polling for document status, invalidation |
| UI state | Zustand | Rail expansion, panel open, sheets, filters |
| Component primitives | Radix UI | Unstyled and accessible; the design is fully custom |
| Styling | CSS Modules + CSS custom properties | [ADR-0004](adr/adr-0004-css-modules-over-tailwind.md) |
| Component docs | Storybook | Primitives are documented as they are built |
| Backend | Python 3.11+ / FastAPI | [ADR-0001](adr/adr-0001-react-vite-spa.md) |
| Storage | SQLite + FTS5 | [ADR-0003](adr/adr-0003-sqlite-single-store.md) |
| Extraction | PyMuPDF, pdfplumber | Deterministic; [ADR-0002](adr/adr-0002-deterministic-extraction.md) |
| LLM access | Gateway over Ollama + Claude | [ADR-0006](adr/adr-0006-llm-gateway.md) |
| Assistant streaming | AG-UI protocol over SSE | [ADR-0009](adr/adr-0009-ag-ui-protocol.md) |
| Agent loop | Plain FastAPI — no framework | [ADR-0010](adr/adr-0010-no-agent-framework.md) |
| Testing | Vitest + Testing Library, Playwright, pytest | |

## Repository layout

A plain workspace, not an Nx monorepo — two apps and a small shared library do not need
a build orchestrator.

```
dm_assistant/
├── docs/                     # this documentation
├── frontend/
│   ├── src/
│   │   ├── app/              # router, providers, shell
│   │   ├── screens/          # login, campaigns, workspace views
│   │   ├── features/         # documents, characters, factions, quests,
│   │   │                     #   sessions, graph, assistant
│   │   ├── ui/               # Radix wrappers + design-token primitives
│   │   ├── styles/           # tokens.css, reset, global
│   │   └── lib/              # api client, hooks, utils
│   └── vite.config.ts
├── backend/
│   ├── app/
│   │   ├── api/              # routers per resource
│   │   ├── core/             # config, db session
│   │   ├── models/           # SQLAlchemy models
│   │   ├── ingestion/        # extract, chunk, index (no LLM)
│   │   ├── retrieval/        # FTS5 search, context assembly
│   │   └── gateway/          # provider abstraction
│   └── pyproject.toml
└── README.md
```

## Ingestion pipeline

Deterministic end to end. No model is called at any step.

```mermaid
sequenceDiagram
    participant U as GM
    participant API as FastAPI
    participant W as Worker
    participant DB as SQLite

    U->>API: POST /documents (file)
    API->>DB: insert document (status=queued, progress=0)
    API-->>U: 202 + document id
    Note over U,API: UI polls status; upload never blocks

    W->>DB: claim queued document
    W->>DB: status=processing
    W->>W: extract text (PyMuPDF / pdfplumber)
    W->>W: split into chunks with headings + page spans
    W->>DB: insert chunks
    W->>DB: populate FTS5 index
    W->>DB: status=indexed, progress=100
```

Failure sets `status=failed` and records `error`. Progress is written per processed page
so the design's percentage bar reflects real work.

## Retrieval and grounding

```mermaid
sequenceDiagram
    participant U as GM
    participant API as FastAPI
    participant R as Retrieval
    participant DB as SQLite
    participant GW as Gateway

    U->>API: POST /assistant/messages
    API-->>U: AG-UI: RunStarted
    API->>R: search(campaign, query)
    API-->>U: AG-UI: ToolCallStart
    R->>DB: FTS5 query over chunks
    DB-->>R: ranked chunks
    R-->>API: context + citations
    API-->>U: AG-UI: ToolCallResult
    API->>GW: prompt(context, question)
    GW-->>API: token stream
    API-->>U: AG-UI: TextMessageContent (delta, repeated)
    API-->>U: AG-UI: Custom dm.citation
    API-->>U: AG-UI: RunFinished
```

Every arrow back to the GM is an **AG-UI event**; everything between API, Retrieval, and
Gateway is our own code. The protocol governs the wire, not the logic
([ADR-0009](adr/adr-0009-ag-ui-protocol.md), [ADR-0010](adr/adr-0010-no-agent-framework.md)).

**The grounding rule.** The prompt instructs the model to answer only from supplied
context and to state plainly when the context does not contain the answer (PRIN-001,
AC-003). Retrieved chunk ids are returned with the response and stored as citations, so
every factual claim is traceable to a source.

GM-private `notes` are excluded from retrieval context by default (DEC-004).

## One request, end to end

What actually happens when a GM types a question. **Only the middle band is AG-UI** — the
protocol owns the events on the wire and nothing else. Retrieval, the prompt, the provider
call, and the loop are all our own code ([ADR-0010](adr/adr-0010-no-agent-framework.md)).

```mermaid
flowchart TB
    subgraph OURS_FE["Our code — frontend"]
        UI["AI panel<br/>bubbles, tool chips, cursor"]
        HOOK["useAssistantStream<br/>fetch + event reader"]
    end

    subgraph PROTO["AG-UI — the wire, and only the wire"]
        EV["RunStarted · ToolCallStart · ToolCallResult<br/>TextMessageStart · TextMessageContent · TextMessageEnd<br/>Custom: dm.citation · RunFinished · RunError"]
    end

    subgraph OURS_BE["Our code — backend (no agent framework)"]
        EP["POST /assistant/messages<br/>the loop, ~40 lines"]
        RET["Retrieval<br/>FTS5 over chunks"]
        GW["LLM Gateway<br/>owns the grounding prompt"]
    end

    subgraph EXT["Provider — swappable"]
        PROV["Ollama · Claude"]
    end

    DB[("SQLite + FTS5")]

    UI -->|"question"| HOOK
    HOOK -->|"POST, SSE open"| EP
    EP -->|"1 · search(campaign, query)"| RET
    RET -->|"2 · ranked chunks"| DB
    DB -->|"3 · chunks + page spans"| RET
    RET -->|"4 · context + citations"| EP
    EP -->|"5 · prompt(context, question)"| GW
    GW -->|"6 · provider call"| PROV
    PROV -->|"7 · token stream"| GW
    GW -->|"8 · normalised tokens"| EP
    EP -->|"9 · emit events"| EV
    EV -->|"10 · typed events"| HOOK
    HOOK -->|"11 · render"| UI

    style PROTO fill:#c6dcff,stroke:#305bab
    style OURS_BE fill:#fff6b6,stroke:#af7e02
    style OURS_FE fill:#e7e7e7,stroke:#595959
    style EXT fill:#dedaff,stroke:#6631d7
    style GW fill:#f8d3af,stroke:#9b4a07
    style RET fill:#adf0c7,stroke:#087429
```

### What owns what

| Layer | Owns | Does **not** own |
|-------|------|------------------|
| **AG-UI** | The event names and shapes crossing the wire | Retrieval, prompting, the loop, provider access |
| **Our endpoint** | The loop: retrieve → prompt → stream → emit | How search works; how providers differ |
| **Gateway** | Provider access **and the grounding prompt** | What gets retrieved |
| **Retrieval** | Chunk selection and ranking | Anything a model touches |

**There is no agent framework in this picture, deliberately.** LangChain, LangGraph, and
Pydantic AI would each take over the loop in step 5 — and with it the prompt assembly,
which is the one place PRIN-001's grounding rule is enforced. With one assistant and one
tool, that loop is a few dozen readable lines. See
[ADR-0010](adr/adr-0010-no-agent-framework.md).

**Where a framework would slot in**, if it ever earns its place: between the endpoint and
the Gateway, owning steps 5 through 8. The Gateway boundary is what keeps that swap
possible without touching the frontend, since AG-UI events would still be what reaches the
wire.

## Frontend state

Three distinct concerns, deliberately not merged:

- **Server state** — TanStack Query. Campaigns, entities, documents, messages. Document
  status polls while any document is `queued` or `processing`, then stops.
- **UI state** — Zustand. `navHover`, `navPinned`, `panelOpen`, `moreOpen`, `mob`,
  filters, composer visibility. Ephemeral, never persisted.
- **Streaming** — an `EventSource` per in-flight assistant message, appending tokens to
  the message being rendered.

The prototype holds all of this in one class component. That is correct for a prototype
and wrong for the app: server data and UI chrome have different lifetimes.

## Boundaries that matter

**BND-001 — No model in the ingestion path.** Enforced structurally: `ingestion/` has no
import path to `gateway/`. A test asserts this.

**BND-002 — All model calls go through the Gateway.** No provider SDK is imported outside
`gateway/`. Provider switching is configuration, not code.

**BND-003 — Campaign scoping is enforced server-side.** Every query filters by
`campaign_id`. The frontend never sees another campaign's data.

**BND-006 — No agent framework owns the loop.** The retrieve-prompt-stream loop is plain
code in `api/assistant.py`. A framework there would also own prompt assembly, moving the
grounding rule out of the single place that enforces it
([ADR-0010](adr/adr-0010-no-agent-framework.md)).

**BND-005 — Provider streams are normalised inside the Gateway.** Model-provider event
shapes never reach the wire; the Gateway converts them to AG-UI events, so switching
providers cannot change what the frontend sees
([ADR-0009](adr/adr-0009-ag-ui-protocol.md)).

**BND-004 — The design prototype is never imported.** `Referee Workspace.dc.html` and
`support.js` are references. Values are transcribed into tokens; markup is rebuilt.
