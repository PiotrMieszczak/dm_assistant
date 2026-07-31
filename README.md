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
| [Design spec](docs/design/design-spec.md) | Screens, layout, and interaction behaviour |
| [Design tokens](docs/design/design-tokens.md) | Colors, type, spacing, radii, shadows |
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

The interface is defined by a high-fidelity design that is the source of truth for
layout, tokens, and interaction. The prototype is a **reference**, not production code —
its values are transcribed into design tokens and its markup is rebuilt with the
project's own primitives.

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

## Relationship to referee-assistant

This project replaces the `referee-assistant` proof of concept. The POC's architecture,
agent model, and technical guides are **not** carried forward — only the product intent
and the design that came out of it.
