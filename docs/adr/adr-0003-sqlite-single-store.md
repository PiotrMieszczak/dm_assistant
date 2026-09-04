---
title: "ADR-0003: SQLite as the single data store; no graph database in v1"
status: "Accepted"
date: "2026-07-31"
authors: "Piotr Mieszczak"
tags: ["architecture", "decision", "storage", "database"]
supersedes: ""
superseded_by: ""
---

# ADR-0003: SQLite as the single data store; no graph database in v1

## Status

Proposed | **Accepted** | Rejected | Superseded | Deprecated

## Context

The product stores campaigns, characters, factions, quests, sessions, documents, chunks,
and the relationships between entities. The design includes an interactive knowledge
graph showing how characters and factions connect.

Prior planning documents specified Neo4j for the knowledge graph alongside SQLite for
metadata and a vector database for embeddings — three stores.

Constraints:

- **CON-001**: The product is local-first and single-user (PRIN-004). Every additional
  store is something the user must install and run.
- **CON-002**: Realistic data volume per campaign is small — dozens of characters, a
  handful of factions, hundreds of relationship edges. Documents produce more rows, but
  chunks are a flat table, not a graph.
- **CON-003**: The graph view's queries are shallow: render all nodes and edges for a
  campaign; show one entity's direct connections. Neither needs traversal beyond one hop.
- **CON-004**: The earlier planning already tagged the knowledge graph as post-MVP, while
  simultaneously specifying its database as infrastructure.

## Decision

**SQLite is the only data store.** Relationships are rows in a `relationship` table with
polymorphic source and target columns. Full-text search uses SQLite's built-in FTS5.
Uploaded files sit on disk with paths recorded in the database.

No Neo4j. No separate vector database. No external database server.

## Consequences

### Positive

- **POS-001**: Zero operational setup. The database is a file; the application creates it
  on first run. Nothing to install, configure, or keep running.
- **POS-002**: One transactional boundary. Creating a character and its relationships is
  atomic — no cross-store consistency problem.
- **POS-003**: Backup and portability are trivial: copy one file and the uploads
  directory.
- **POS-004**: FTS5 is compiled into SQLite, so full-text search needs no additional
  dependency (ADR-0005).
- **POS-005**: Development and test setup are trivial; tests run against a temporary file
  or in-memory database.

### Negative

- **NEG-001**: Deep graph traversal ("everyone within three degrees of the Pale Court")
  requires recursive CTEs, which are more awkward than Cypher and slower at scale.
- **NEG-002**: Graph layout is computed client-side rather than by a graph engine.
  Acceptable at expected node counts; it would not be at thousands of nodes.
- **NEG-003**: SQLite's write concurrency is limited. The ingestion worker and API writing
  simultaneously requires WAL mode and care.
- **NEG-004**: If semantic search is added later, either a vector extension
  (`sqlite-vec`) or a separate store must be introduced then.

## Alternatives Considered

### Neo4j for relationships, SQLite for everything else

- **ALT-001**: **Description**: As specified in earlier planning — a dedicated graph
  database backing the knowledge graph, with SQLite holding metadata.
- **ALT-002**: **Rejection Reason**: Requires the user to run a database server for a
  feature whose queries are one hop deep over a few hundred edges. Introduces
  cross-store consistency burden with no capability gain at this scale. Contradicts
  local-first (CON-001).
- **ALT-011**: **A graph-shaped domain does not imply a graph database.** This is the
  argument that keeps resurfacing, so it is worth stating plainly. Characters, factions,
  and their edges genuinely form a graph — but what selects a database is the shape of the
  **queries**, not the shape of the data. Every query the design asks for is zero or one
  hop: render all nodes and edges for a campaign (`SELECT * FROM relationship WHERE
  campaign_id = ?`), list one entity's direct connections, highlight nodes matching a
  search. A graph database earns its cost on deep traversal — "everyone within three
  degrees of the Pale Court, weighted by relationship kind" — which is a painful recursive
  CTE in SQL and a one-line Cypher query. Nothing in this product asks that. Until
  something does, a graph database buys syntax, not capability.

### PostgreSQL as a single store

- **ALT-003**: **Description**: One server-based database, with `pgvector` and full-text
  search available if needed later.
- **ALT-004**: **Rejection Reason**: Better than a multi-store setup, but still a server
  the user must run for a single-user local tool. Revisit if the product ever becomes
  hosted or multi-user.

### SQLite plus a dedicated vector store from day one

- **ALT-005**: **Description**: Add Chroma or LanceDB alongside SQLite for embeddings.
- **ALT-006**: **Rejection Reason**: Premature — see [ADR-0005](adr-0005-fts5-before-vectors.md).
  Keyword retrieval has not yet been shown to be insufficient.

## Implementation Notes

- **IMP-001**: Enable WAL mode and set a busy timeout so the ingestion worker and API can
  write concurrently (addresses NEG-003).
- **IMP-002**: `relationship` rows are stored once per pair and resolved bidirectionally
  on read; the graph treats edges as undirected.
- **IMP-003**: Migrations are versioned from the start, even for a local file database —
  schema changes must not require users to discard their campaigns.
- **IMP-004**: The graph endpoint returns nodes and edges pre-shaped for rendering, so
  the client does no relational assembly.
- **IMP-005**: Revisit trigger — if graph queries exceed two hops, or if a campaign's
  edge count makes the graph endpoint slow, reassess. Measure before migrating.

## References

- **REF-001**: `docs/data-model.md` — the resulting schema
- **REF-002**: [ADR-0005](adr-0005-fts5-before-vectors.md) — FTS5 retrieval decision
- **REF-003**: `docs/mvp-scope.md` — deferral of the graph database with revisit trigger
