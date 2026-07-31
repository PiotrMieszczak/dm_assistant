---
title: "ADR-0001: React + Vite SPA with FastAPI backend"
status: "Accepted"
date: "2026-07-31"
authors: "Piotr Mieszczak"
tags: ["architecture", "decision", "stack", "frontend", "backend"]
supersedes: ""
superseded_by: ""
---

# ADR-0001: React + Vite SPA with FastAPI backend

## Status

Proposed | **Accepted** | Rejected | Superseded | Deprecated

## Context

DM Assistant is a fresh build replacing the `referee-assistant` proof of concept. The
POC was Vue 3 + Nx + FastAPI, but its frontend was the only layer with real substance —
the backend was a health endpoint and an in-memory list. Nothing in it is being carried
forward.

Constraints shaping this decision:

- **CON-001**: The design (`Referee Workspace.dc.html`) is a stateful client
  application — login → campaign picker → workspace, with rail expansion, panel
  toggles, sheets, and filters all held as client state.
- **CON-002**: There is no SEO requirement. The tool is single-user and local-first
  (PRIN-004); no page needs to be crawlable or server-rendered for discovery.
- **CON-003**: Document processing requires PyMuPDF, pdfplumber, and potentially spaCy
  and OCR tooling. This ecosystem is Python-native and materially weaker in JavaScript.
- **CON-004**: Prior planning documents specified Next.js 15 with React Server
  Components, written before the design existed.

## Decision

The frontend is a **React 19 + TypeScript single-page application built with Vite**,
routed by React Router v7. The backend is **Python 3.11+ with FastAPI**, serving a JSON
API consumed by the SPA.

Next.js is rejected. The design has no server-rendering requirement, and FastAPI already
owns the API layer — a Next.js server would add a second backend process with almost no
responsibility, plus the client/server component boundary as ongoing complexity.

## Consequences

### Positive

- **POS-001**: One backend. FastAPI owns all server responsibility; there is no ambiguity
  about where logic belongs or duplicated API surface across two runtimes.
- **POS-002**: Document processing runs in its natural ecosystem. PyMuPDF and pdfplumber
  are used directly rather than reimplemented or shelled out to.
- **POS-003**: Vite's dev server and HMR are fast, and the build is a static bundle that
  can be served by anything — including FastAPI itself in a local-first deployment.
- **POS-004**: No client/server component split. Every component is a client component;
  there is no serialization boundary to reason about.
- **POS-005**: Client-side state maps directly onto the design's model, which is
  expressed as one state object driving all screens.

### Negative

- **NEG-001**: No server-side rendering. First paint waits on the JavaScript bundle.
  Acceptable for a single-user local tool; it would not be for a public product.
- **NEG-002**: Two languages and two toolchains. Shared types between frontend and
  backend must be maintained deliberately — the API contract is documented rather than
  derived from a shared source.
- **NEG-003**: Departs from prior planning documents that specified Next.js, which are
  now superseded.
- **NEG-004**: Two processes to run in development.

## Alternatives Considered

### Next.js 15 with App Router

- **ALT-001**: **Description**: React with file-based routing, Server Components, and
  route handlers, as specified in the earlier epic.
- **ALT-002**: **Rejection Reason**: Adds a Node server with nothing substantial to do —
  FastAPI must exist regardless for document processing. The RSC boundary is real
  complexity, paid for benefits (SSR, SEO, streaming HTML) that a local single-user tool
  does not need.

### Vue 3, continuing the POC stack

- **ALT-003**: **Description**: Keep Vue and reuse the POC's `ra-ui` library, design
  system SCSS, and chat components.
- **ALT-004**: **Rejection Reason**: The decision to move to React was already made and
  documented before this ADR. The new design supersedes the POC's interface entirely, so
  the reusable surface is smaller than it appears — the design tokens port regardless of
  framework, and the components would need rebuilding either way.

### Full-TypeScript stack (Node/Hono backend)

- **ALT-005**: **Description**: One language across frontend and backend, with shared
  types and a single toolchain.
- **ALT-006**: **Rejection Reason**: PDF extraction and NLP tooling in JavaScript is
  substantially weaker than Python's. The core differentiator would be built on the
  weaker foundation to gain type sharing — the wrong trade for this product.

## Implementation Notes

- **IMP-001**: TypeScript runs in strict mode with `noUncheckedIndexedAccess` and
  `exactOptionalPropertyTypes`.
- **IMP-002**: The API contract in `docs/api-contract.md` is the coordination point
  between the two stacks. Consider generating a client from FastAPI's OpenAPI schema to
  reduce NEG-002 drift.
- **IMP-003**: Layout is a plain workspace — `frontend/` and `backend/` — not an Nx
  monorepo. Two applications and one small shared library do not justify a build
  orchestrator.
- **IMP-004**: If SSR is ever needed, the SPA can be migrated behind a framework without
  changing the backend, since all server logic already lives in FastAPI.

## References

- **REF-001**: [ADR-0002](adr-0002-deterministic-extraction.md) — extraction approach
  that motivates the Python backend
- **REF-002**: `docs/architecture.md` — resulting system shape
- **REF-003**: Claude Design project `ec1d38ec-c81f-42b8-8952-7a922851f405`
