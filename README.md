# dm_assistant

An in-session workspace for tabletop RPG game masters: campaign material on the left,
an assistant grounded in that material on the right.

Upload your rulebooks, modules, and notes; they are extracted and indexed. During a
session, ask questions in natural language and get answers drawn from **your** books,
with sources shown. Around that sits the workspace for running a game — NPCs, players,
factions, a quest log, session records, and a knowledge graph of how everyone connects.

## Status

**Pre-implementation.** This repository currently contains documentation only. No
application code has been written yet.

Start with [docs/README.md](docs/README.md).

## Documentation

| Document | What it answers |
|----------|-----------------|
| [Product brief](docs/product-brief.md) | What we are building, for whom, and why |
| [MVP scope](docs/mvp-scope.md) | What ships in v1 and what explicitly does not |
| [Data model](docs/data-model.md) | Entities, relationships, and storage |
| [Architecture](docs/architecture.md) | System shape, stack, and boundaries |
| [Folder structure](docs/folder-structure.md) | Folder layout and dependency rules for both apps |
| [Design spec](docs/design/overview.md) | Screens, layout, and interaction behaviour |
| [Design tokens](docs/design/reference.md) | Colors, type, spacing, radii, shadows |
| [API contract](docs/api-contract.md) | HTTP surface between frontend and backend |
| [Roadmap](docs/roadmap.md) | Delivery phases and acceptance gates |
| [ADRs](docs/adr/) | Architectural Decision Records |

## Planned stack

| Layer | Choice |
|-------|--------|
| Frontend | React 19 + TypeScript + Vite, React Router v7 |
| Styling | CSS Modules over CSS custom properties — **no Tailwind** |
| Components | Radix UI primitives, documented in Storybook |
| State | TanStack Query (server) + Zustand (UI) |
| Backend | Python 3.11+ / FastAPI |
| Storage | SQLite with FTS5 |
| Extraction | PyMuPDF, pdfplumber — deterministic, no LLM |
| AI | Gateway over Ollama and Claude |

See [ADR-0001](docs/adr/adr-0001-react-vite-spa.md) for the stack rationale.

## Design

**▶ [Open the interactive design](https://claude.ai/code/artifact/a7d4de30-0826-4747-b295-a584fe6f0f28)**

The running prototype, and the source of truth for layout, tokens, and interaction. Click
through it — login, campaign picker, the workspace views, the graph, and the mobile shell
below 900px. Interaction is most of what this design specifies, so a screenshot would
convey little of it.

It is a **reference, not production code**: values are transcribed into
[design tokens](docs/design/reference.md) and markup is rebuilt with the project's own
primitives.

## Architecture at a glance

**▶ [Open the architecture board](https://miro.com/app/board/uXjVHrcVIJQ=/)**

A Miro board with the system shape and both data flows — ingestion and retrieval —
mirroring [docs/architecture.md](docs/architecture.md). Useful for walking someone through
the two boundaries that define this system: extraction never calls a model, and every
model call goes through one gateway.

## Folder structure

Two applications, one dependency direction: volatile things at the edge, stable things at
the centre, every arrow pointing inward. Full layout and the enforced import rules are in
[docs/folder-structure.md](docs/folder-structure.md).

**Backend — hexagonal (ports and adapters).** The domain knows nothing about the world.

```
backend/app/
├── domain/          # entities, value objects, invariants. Pure — no I/O, no framework.
├── ports/           # interfaces the domain declares: repositories, search, llm,
│                    #   extraction, files, clock
├── application/     # use cases. Orchestrates domain + ports; never imports an adapter.
├── adapters/        # the outside world — the only place SDKs are imported
│   ├── persistence/ #   sqlalchemy/ + memory/ (the fast test double)
│   ├── search/      #   fts5/ + memory/
│   ├── llm/         #   claude, ollama, fake, prompts per mode
│   └── extraction/  #   pymupdf, ocr
├── entrypoints/     # driving adapters: http/, worker/, cli/. Transport only.
└── composition.py   # the ONLY module wiring ports to adapters
```

```
entrypoints ──→ application ──→ ports ←── adapters
                     │           │          │
                     └───────────┴──→ domain ┘
```

**Frontend — domain-oriented split.** Bounded contexts with published interfaces.

```
frontend/src/
├── app/         # router, providers, shell
├── domains/     # campaign · cast · world · adventure · library · graph · assistant
│   └── <ctx>/   #   model/ · api/ · components/ · store.ts · index.ts ← public API
├── screens/     # routed pages. Compose domains, own no logic.
├── ui/          # design-system primitives. Knows no domain.
├── styles/      # tokens.css, reset, global
└── lib/         # http client, SSE reader, utils
```

**One rule does most of the work:** a domain may only be imported through its `index.ts`.
Deep imports are what turn a domain split into a ball of mud. Both rule sets run in CI —
`import-linter` on Python, `eslint-plugin-boundaries` on TypeScript — so a violation fails
the build rather than drifting quietly.

## Two ideas worth knowing up front

**Extraction never uses a language model.** Parsing is deterministic, so the index
contains only text that is genuinely in your documents. That is what makes citations
trustworthy. Models are used at query time only.
See [ADR-0002](docs/adr/adr-0002-deterministic-extraction.md).

**Infrastructure is deferred with a trigger, not by silence.** No graph database, no
vector store in v1 — each has a written condition that would justify adding it, and the
instrumentation to detect that condition is part of the work.
See [ADR-0003](docs/adr/adr-0003-sqlite-single-store.md) and
[ADR-0005](docs/adr/adr-0005-fts5-before-vectors.md).
