---
title: "ADR-0005: FTS5 keyword retrieval before semantic search"
status: "Accepted"
date: "2026-07-31"
authors: "Piotr Mieszczak"
tags: ["architecture", "decision", "retrieval", "search"]
supersedes: ""
superseded_by: ""
---

# ADR-0005: FTS5 keyword retrieval before semantic search

## Status

Proposed | **Accepted** | Rejected | Superseded | Deprecated

## Context

The assistant answers questions grounded in indexed campaign material. Something must
select which chunks become context for a given question.

The default assumption in retrieval-augmented systems is vector search: embed every
chunk, embed the query, retrieve by cosine similarity. Earlier planning listed a vector
database as infrastructure, though marked optional in places.

Constraints:

- **CON-001**: Queries are largely terminological. A GM asks about *opportunity attacks*,
  *Doran Vey*, or *the Pale Court* — proper nouns and rulebook terms of art that appear
  verbatim in the source.
- **CON-002**: Embedding every chunk of a 400-page rulebook costs either API calls or a
  local embedding model, on every upload — reintroducing the per-page cost that
  [ADR-0002](adr-0002-deterministic-extraction.md) deliberately avoided.
- **CON-003**: FTS5 ships inside SQLite. It requires no additional dependency, service,
  or model ([ADR-0003](adr-0003-sqlite-single-store.md)).
- **CON-004**: Retrieval quality has not been measured. No evidence yet exists that
  keyword search is insufficient for this corpus and these queries.

## Decision

**Retrieval uses SQLite FTS5 over chunk text.** Semantic search is not implemented in v1.

The deferral is conditional, not permanent. Vector search is added when keyword retrieval
is **measured** to fail on real queries — specifically, when paraphrased questions that a
GM would plausibly ask fail to retrieve chunks that demonstrably contain the answer.

## Consequences

### Positive

- **POS-001**: No embedding cost at ingestion. Indexing stays deterministic, fast, and
  free, consistent with ADR-0002.
- **POS-002**: No additional dependency, service, or model to install or run.
- **POS-003**: Exact-term matching is a genuine strength for this corpus. Proper nouns and
  rulebook terminology are precisely where keyword search outperforms embeddings, which
  can retrieve semantically adjacent but factually wrong passages.
- **POS-004**: Results are explainable. A matched chunk contains the queried terms, and
  FTS5 snippet generation produces highlightable excerpts directly.
- **POS-005**: The retrieval interface is narrow, so substituting or supplementing the
  implementation later touches one module.

### Negative

- **NEG-001**: Paraphrased queries can miss. Asking "what happens if I walk away from a
  monster" may not retrieve a chunk that only says "opportunity attack".
- **NEG-002**: No conceptual similarity. Related passages that share no vocabulary with
  the query are not retrieved.
- **NEG-003**: Synonym handling requires explicit work — stemming and query expansion
  rather than learned representation.
- **NEG-004**: Retrieval quality depends on chunk boundaries aligning with topics, which
  heuristic chunking does imperfectly.

## Alternatives Considered

### Vector search from the start

- **ALT-001**: **Description**: Embed all chunks at ingestion; retrieve by vector
  similarity using `sqlite-vec`, Chroma, or LanceDB.
- **ALT-002**: **Rejection Reason**: Reintroduces per-document processing cost (CON-002)
  and a dependency, to solve a problem not yet shown to exist (CON-004). Embedding models
  also retrieve plausible-but-wrong passages, which is a specific hazard for rules
  questions where near-miss answers are actively harmful.

### Hybrid keyword + vector with reciprocal rank fusion

- **ALT-003**: **Description**: Run both retrievers and fuse the rankings.
- **ALT-004**: **Rejection Reason**: The likely long-term answer, and the intended
  evolution — but it presumes the vector half, whose cost and benefit are unmeasured.
  Building both before measuring either means never learning which one carries the
  quality.

### LLM-based retrieval (ask the model to pick relevant sections)

- **ALT-005**: **Description**: Present section headings to a model and let it choose
  what to read.
- **ALT-006**: **Rejection Reason**: Cost scales with corpus size per query, latency is
  poor for live session use (PRIN-003), and selection quality varies by provider — an
  acute problem given Ollama support (ADR-0006).

## Implementation Notes

- **IMP-001**: Retrieval lives behind a single interface in `backend/app/retrieval/` so
  the implementation can be extended without touching callers.
- **IMP-002**: Use FTS5 with the `porter` tokenizer for basic stemming, partially
  mitigating NEG-003.
- **IMP-003**: Use `snippet()` and `bm25()` for excerpt generation and ranking.
- **IMP-004**: Log queries that return no results or whose answers the user rejects.
  This is the measurement that makes the revisit trigger real rather than rhetorical —
  without it, "measure first" becomes "never revisit".
- **IMP-005**: Build a small evaluation set of question/expected-chunk pairs against the
  fixture corpus. Adding vector search should have to demonstrate improvement against it.
- **IMP-006**: When vector search is added, prefer `sqlite-vec` to preserve the
  single-store property of ADR-0003.

## References

- **REF-001**: [ADR-0002](adr-0002-deterministic-extraction.md) — deterministic ingestion
- **REF-002**: [ADR-0003](adr-0003-sqlite-single-store.md) — single-store decision
- **REF-003**: `docs/mvp-scope.md` — deferral with revisit trigger
- **REF-004**: `docs/architecture.md` — retrieval and grounding flow
