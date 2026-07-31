# MVP Scope

The design defines the **target product**. This document defines what **v1 ships**.

Every screen in the design is built — the design is the source of truth for the
interface. The distinction is how much *behaviour* sits behind each screen in v1.

## Scope tiers

| Tier | Meaning |
|------|---------|
| **Full** | Built to the design, backed by real persistence and real logic |
| **Local** | Built to the design, persisted locally, no AI or derived behaviour |
| **Read-only** | Built to the design, renders real data, editing deferred |
| **Deferred** | Not in v1; route exists and states it is coming |

## In scope

### Shell and navigation — Full

- Login screen (local profile; no real auth — see PRIN-004)
- Campaign picker with add-campaign modal (image + mandatory system)
- App shell: 72px header, floating nav rail (60px ↔ 236px), AI panel column
- Mobile shell ≤900px: bottom tab bar, More sheet, AI slide-over
- Settings: account fields and AI provider selection

### Documents — Full

The differentiating capability. Upload → extract → index → retrieve.

- Upload PDF, Markdown, and plain text
- Deterministic extraction (PyMuPDF / pdfplumber), chunking, SQLite FTS5 indexing
- Background processing with live status: `Queued` → `Processing` (%) → `Indexed` / `Failed`
- Document list exactly as designed, including per-item progress
- Full-text search across a campaign's indexed material

### Assistant — Full

- Chat panel with streaming responses
- Retrieval grounded in the active campaign's indexed chunks, with citations
- LLM Gateway abstracting provider; Ollama and Claude both selectable at runtime
- Tool-call indicator chips (the design's green check rows) for retrieval steps
- Quick-prompt chips, typing indicator, attach affordance

### NPCs, Players, Factions — Full

The design models these as one `Character` entity split by an `isPlayer` flag, plus a
separate `Faction` entity. All support create, read, update, delete, plus portrait upload.

- NPC list with relationship filters (all / ally / enemy / family / professional / neutral)
- Player list and Add Player form
- Faction list and detail, with members and inter-faction relationships
- Character detail: stats, connections, quote, GM notes, disposition

### Quests — Full

- Five-status quest log (available, in progress, completed, failed, inactive)
- Progress counters (`cur` / `max`) with progress bars
- Parent/subquest relationships
- Create, edit, status transitions, reactivate

### Sessions — Full

- Session log list
- Rich-text composer for session entries
- Entries are indexed alongside documents and become retrievable material

### Knowledge Graph — Read-only

Rendered from real relationship data, not mock data.

- Force-directed layout of characters and factions
- Relationship-coloured edges with legend
- Search highlights matches and dims the rest
- Hover info card; click navigates to entity detail
- **Deferred:** editing relationships from the graph; graph-backed AI queries

## Out of scope for v1

| Item | Why | Revisit when |
|------|-----|--------------|
| **Neo4j / graph database** | Relationship counts at single-campaign scale are trivial for SQLite. A dedicated graph DB is operational weight with no payoff yet. See [ADR-0003](adr/adr-0003-sqlite-single-store.md). | Graph queries exceed 2 hops or performance degrades |
| **Vector search / embeddings** | FTS5 keyword retrieval is the honest first attempt. Add semantic search when keyword search is demonstrably insufficient — measured, not assumed. See [ADR-0005](adr/adr-0005-fts5-before-vectors.md). | Retrieval quality measurably fails on paraphrased queries |
| **OCR for scanned PDFs** | Native-text PDFs cover the common case. OCR adds a heavy dependency chain. The design's `Queued` + "awaiting OCR" state is built; the processor is not. | Users upload scanned material in practice |
| **Multi-agent orchestration** | One assistant with retrieval tools is simpler and easier to evaluate than five agents behind an intent router. | A single agent measurably underperforms on distinct task types |
| **Real authentication** | Local-first, single-user. The login screen is a shell. | Multi-user or hosted deployment is on the table |
| **Automatic entity extraction from PDFs** | Auto-creating NPCs from a module is attractive and unreliable. Manual entry first; the extraction path stays open. | Extraction accuracy can be measured against a fixture corpus |
| **Session recap generation** | Depends on a corpus of session logs existing first. | Session logs are in regular use |
| **Plot analysis / suggestions** | Same dependency, plus a much fuzzier success criterion. | Core retrieval is trusted |

## Acceptance criteria for v1

The MVP is done when all of the following hold:

- **AC-001** A GM uploads a 400-page PDF; it reaches `Indexed` without manual steps, and
  progress is visible throughout.
- **AC-002** A rules question against indexed material returns a grounded answer citing
  its source chunk.
- **AC-003** Asking about material that was never indexed produces an explicit "not in
  your material" response, not a plausible invention.
- **AC-004** Switching the provider between Claude and Ollama in Settings changes which
  backend serves the next message, with no code change or restart.
- **AC-005** Characters, factions, and quests survive a restart (real persistence).
- **AC-006** The knowledge graph renders actual relationships from stored data.
- **AC-007** Every designed screen matches the spec's tokens, spacing, and states at both
  desktop and ≤900px.
- **AC-008** Document processing never blocks the UI.

## Deliberately unresolved

The design has no screen for these; they need design work before implementation:

- **Upload progress at the moment of upload** — the list shows status, but the
  drag-and-drop / file-picker interaction and its immediate feedback are unspecified.
- **Extraction failure** — no designed state for a PDF that cannot be parsed. v1 needs a
  `Failed` treatment with a retry affordance.
- **Empty states** — no designed empty state for a new campaign with no documents, NPCs,
  factions, or quests. This is the *first* thing a new user sees.
- **Citation presentation** — the assistant must show sources (AC-002), but the design
  does not specify how a citation renders inside a chat bubble.
