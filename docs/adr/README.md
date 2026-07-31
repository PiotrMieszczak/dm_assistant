# Architectural Decision Records

Decisions that constrain implementation live here, not scattered through prose. If a
choice would surprise a new contributor, or if someone might reasonably undo it without
knowing why it was made, it belongs in an ADR.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](adr-0001-react-vite-spa.md) | React + Vite SPA with FastAPI backend | Accepted |
| [0002](adr-0002-deterministic-extraction.md) | Deterministic document extraction, no LLM in the ingestion path | Accepted |
| [0003](adr-0003-sqlite-single-store.md) | SQLite as the single data store; no graph database in v1 | Accepted |
| [0004](adr-0004-css-modules-over-tailwind.md) | CSS Modules over design tokens; Tailwind excluded | Accepted |
| [0005](adr-0005-fts5-before-vectors.md) | FTS5 keyword retrieval before semantic search | Accepted |
| [0006](adr-0006-llm-gateway.md) | Centralized LLM Gateway with runtime provider switching | Accepted |

## Format

Records follow the structure documented in the `adr` plugin
(see the `llm_utils` marketplace):

- YAML frontmatter: `title`, `status`, `date`, `authors`, `tags`, `supersedes`,
  `superseded_by`
- Sections: Status, Context, Decision, Consequences (positive and negative),
  Alternatives Considered, Implementation Notes, References
- **Coded bullets** — `CON-001`, `POS-001`, `NEG-001`, `ALT-001`, `IMP-001`, `REF-001`.
  Stable identifiers let later records cite a specific point precisely
  ("supersedes ADR-0005 NEG-001") and make records greppable.

Filename convention: `adr-NNNN-[title-slug].md`, sequential four-digit numbering.

## Status values

| Status | Meaning |
|--------|---------|
| **Proposed** | Under discussion; not yet binding |
| **Accepted** | In force; implementation should follow it |
| **Rejected** | Considered and declined; kept so it is not re-litigated |
| **Superseded** | Replaced by a later ADR, named in `superseded_by` |
| **Deprecated** | No longer applies, with no direct replacement |

Records are immutable once accepted. A changed decision means a **new ADR** that
supersedes the old one — the history of why is as valuable as the current state.

## Decision themes in this set

Two threads run through these records and are worth reading together:

**Where AI is and is not used.** [ADR-0002](adr-0002-deterministic-extraction.md) bars
models from ingestion; [ADR-0006](adr-0006-llm-gateway.md) confines them to a single
gateway at query time. Both are enforced by architectural tests rather than convention,
because both erode the first time someone adds "just one small call".

**Deferral with a trigger, not deferral by silence.**
[ADR-0003](adr-0003-sqlite-single-store.md) and
[ADR-0005](adr-0005-fts5-before-vectors.md) each decline infrastructure that earlier
planning treated as given — a graph database and a vector store. Neither is rejected
outright; each names the measurement that would justify revisiting. The instrumentation
to make those measurements is itself an implementation note, so "measure first" does not
quietly become "never revisit".
