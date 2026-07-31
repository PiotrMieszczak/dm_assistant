# Roadmap

Phases are ordered by dependency and by what de-risks the product earliest. Each has an
**exit gate** — an observable condition, not a checklist of activity.

Phases are not dated. They are sized relative to one another and gated on evidence.

## Phase 0 — Foundation

Scaffold both applications and the token system.

- Vite + React 19 + TypeScript (strict) frontend; FastAPI backend
- `tokens.css` transcribed from [design-tokens.md](design/design-tokens.md)
- CSS Modules pipeline, no Tailwind ([ADR-0004](adr/adr-0004-css-modules-over-tailwind.md))
- Radix primitives wrapped in `ui/`: Button, Input, Dialog, Tabs, Card, Chip
- Storybook covering each primitive with its designed states
- SQLite schema and migrations from [data-model.md](data-model.md)
- Test harness: Vitest + Testing Library, pytest, Playwright

**Exit gate.** A primitive rendered in Storybook is visually indistinguishable from the
same element in the prototype, and every value it uses comes from a token.

## Phase 1 — Shell and campaigns

The frame everything else renders inside.

- Login screen (local profile)
- Campaign picker, campaign cards, add-campaign modal with mandatory system
- Workspace shell: header, floating nav rail with hover/pin, AI panel column
- Mobile shell: bottom tab bar, More sheet, slide-over panel, `mob` behaviour switch
- Routing `/login`, `/campaigns`, `/c/:campaignId/:view`
- Campaign CRUD end to end

**Exit gate.** A campaign can be created, entered, and switched; the shell matches the
design at desktop and ≤900px, including rail expansion and panel defaults per viewport.

## Phase 2 — Documents and retrieval

The differentiator. Everything downstream depends on this being trustworthy.

- Upload (PDF, Markdown, text) with the missing interaction designed first
- Deterministic extraction, chunking with headings and page spans
  ([ADR-0002](adr/adr-0002-deterministic-extraction.md))
- Background worker with real per-page progress
- FTS5 index and search endpoint ([ADR-0005](adr/adr-0005-fts5-before-vectors.md))
- Documents view with live status, progress bars, and a `Failed` state with retry
- Structural test asserting `ingestion/` cannot import `gateway/` (BND-001)

**Exit gate.** AC-001 and AC-008 — a 400-page PDF reaches `Indexed` unattended with
visible progress, and the UI stays responsive throughout. Search returns the right chunk
for a known question against a fixture corpus.

## Phase 3 — Assistant

Retrieval becomes conversation.

- LLM Gateway with Ollama and Claude behind one interface
  ([ADR-0006](adr/adr-0006-llm-gateway.md))
- Grounded prompting: retrieved context, refusal when context is insufficient
- SSE streaming with token, tool, and citation events
- AI panel: bubbles, tool chips, streaming cursor, typing dots, quick prompts, composer
- Provider switching from Settings, effective without restart
- Citation rendering — requires the design gap to be closed first

**Exit gate.** AC-002, AC-003, AC-004 — grounded answers with visible citations, explicit
refusal on unindexed topics, and live provider switching. Refusal behaviour is verified
against a set of deliberately-unanswerable questions, not assumed.

## Phase 4 — Campaign entities

The session-running surface.

- Characters: NPC list with relationship filters, party list, Add Player, detail views,
  portrait upload
- Factions: list, detail, membership, inter-faction relationships
- Quests: five status tabs, progress, subquests, transitions, reactivate
- Sessions: list, rich-text composer, indexing of session bodies
- Overview: hero, stat grid, recent activity — driven by real counts

**Exit gate.** AC-005 — all entities persist across restart, and every list, detail, and
form matches the design at both breakpoints.

## Phase 5 — Knowledge graph

Last, because it renders relationships the earlier phases create.

- Force-directed layout over real nodes and edges
- Relationship-coloured edges with legend
- Search highlight and dim
- Hover info card; click through to detail

**Exit gate.** AC-006 — the graph renders stored relationships, not fixtures, and
navigation from a node reaches the correct entity.

## Phase 6 — Hardening

- Empty states for every collection (design gap — must be closed)
- Accessibility pass: focus order, keyboard navigation, contrast, 44px touch targets
- Performance: interactions under 300ms (PRIN-003)
- End-to-end Playwright coverage of the core loop
- Error handling: failed uploads, unreachable provider, corrupt files

**Exit gate.** AC-007 plus the full acceptance list in
[mvp-scope.md](mvp-scope.md#acceptance-criteria-for-v1) passing.

## Sequencing rationale

**Why documents before entities.** Retrieval is the risky, differentiating part. If
grounded answers cannot be made trustworthy, that should be discovered in Phase 2 — not
after building five CRUD screens. Manual entity entry is well-understood work with
minimal risk; it can wait.

**Why the graph is last.** It visualises relationships that Phase 4 creates. Building it
earlier means building it against fixtures, then rebuilding it against real data.

**Why design gaps block phases.** Four interactions are unspecified
([design-spec.md](design/design-spec.md#gaps-requiring-design)). Each blocks the phase
that needs it: upload and failure states block Phase 2, citation rendering blocks
Phase 3, and empty states block Phase 6. Building a guess and reworking it later costs
more than a short design pass.

## Deferred work

Items in [mvp-scope.md](mvp-scope.md#out-of-scope-for-v1) each carry a revisit trigger.
None is scheduled. They become candidates only when their trigger is observed — in
particular, vector search waits on measured retrieval failure, and a graph database waits
on measured query cost.
