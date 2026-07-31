---
title: "ADR-0002: Deterministic document extraction, no LLM in the ingestion path"
status: "Accepted"
date: "2026-07-31"
authors: "Piotr Mieszczak"
tags: ["architecture", "decision", "ingestion", "ai-boundary"]
supersedes: ""
superseded_by: ""
---

# ADR-0002: Deterministic document extraction, no LLM in the ingestion path

## Status

Proposed | **Accepted** | Rejected | Superseded | Deprecated

## Context

The product's core capability is answering questions grounded in a game master's own
campaign material — rulebooks, adventure modules, and notes, typically PDFs of a few
hundred pages.

Two approaches exist for turning those files into retrievable text:

1. Parse deterministically with libraries (PyMuPDF, pdfplumber), then chunk and index.
2. Pass pages to a language model and ask it to extract structured content.

The second is increasingly common and superficially attractive: models handle messy
layouts, multi-column text, and tables without bespoke parsing code.

Constraints:

- **CON-001**: A 400-page rulebook is a normal upload. Per-page model calls make
  ingestion cost scale with document size, on every upload.
- **CON-002**: Answers must be trustworthy (PRIN-001). If extraction itself can
  hallucinate, no downstream grounding can recover — the index would contain text that
  was never in the source.
- **CON-003**: Extraction must be testable. Regression testing requires the same input
  to produce the same output.
- **CON-004**: Ollama is a supported provider (ADR-0006). Local models are slower and
  weaker; ingestion that depends on model quality would behave very differently per
  provider.

## Decision

**No language model is invoked anywhere in the ingestion path.** Extraction, parsing,
chunking, and indexing are entirely deterministic, using PyMuPDF and pdfplumber.

Language models act **only at query time**, on already-indexed data.

This boundary is enforced structurally: `backend/app/ingestion/` has no import path to
`backend/app/gateway/`, and a test asserts it (BND-001).

## Consequences

### Positive

- **POS-001**: Ingestion is reproducible. The same PDF always yields the same chunks, so
  extraction regressions are detectable by comparing against fixtures.
- **POS-002**: Ingestion cost is near zero and independent of document size. A GM can
  upload an entire library without cost concern.
- **POS-003**: The index cannot contain hallucinated text. Every indexed chunk is
  literally present in the source, which is what makes citations meaningful.
- **POS-004**: Ingestion behaves identically regardless of the configured provider, and
  works with no provider configured at all.
- **POS-005**: Processing speed is bounded by disk and CPU, not by an API, so real
  per-page progress can be reported (a requirement of the Documents view).

### Negative

- **NEG-001**: Difficult layouts — multi-column spreads, sidebars, stat blocks in tables
  — extract imperfectly. A model would handle some of these better.
- **NEG-002**: Scanned PDFs with no text layer cannot be processed at all without OCR,
  which is deferred. The design's `Queued` / "awaiting OCR" state exists with no
  processor behind it.
- **NEG-003**: Parsing improvements require code, not prompt changes.
- **NEG-004**: Semantic structure (which heading owns which paragraph) is inferred from
  formatting heuristics and will sometimes be wrong.

## Alternatives Considered

### LLM-based extraction

- **ALT-001**: **Description**: Send page images or raw text to a vision or text model
  and ask for structured markdown or JSON.
- **ALT-002**: **Rejection Reason**: Violates CON-002 fatally. If the extractor can
  invent text, the index becomes untrustworthy and citations become meaningless — a
  citation pointing at hallucinated text is worse than no citation. Also fails CON-001
  and CON-003.

### Hybrid — deterministic first, LLM fallback on low-confidence pages

- **ALT-003**: **Description**: Parse deterministically; route pages that appear to
  extract poorly to a model for a second attempt.
- **ALT-004**: **Rejection Reason**: Reintroduces every problem of ALT-002 for an
  unpredictable subset, and makes the index non-uniform — some chunks verbatim, some
  model-generated, with no clear signal to the user which is which. Worth revisiting only
  if such chunks are explicitly marked and excluded from citation.

### LLM for structure only, never content

- **ALT-005**: **Description**: Use deterministic text extraction, but ask a model to
  identify section boundaries and headings.
- **ALT-006**: **Rejection Reason**: Defensible, since content stays verbatim. Deferred
  rather than rejected outright: it still costs per-page calls (CON-001) and varies by
  provider (CON-004). Revisit if heuristic chunking proves to be the limiting factor in
  retrieval quality.

## Implementation Notes

- **IMP-001**: PyMuPDF for native text; pdfplumber for tables and layout-sensitive
  extraction.
- **IMP-002**: Chunks retain `page_from`, `page_to`, and the nearest `heading` so
  citations can point at a specific location.
- **IMP-003**: A fixture corpus of representative PDFs — clean single-column, multi-column,
  table-heavy — anchors extraction regression tests.
- **IMP-004**: The import-boundary test is the enforcement mechanism. Without it, this
  decision erodes the first time someone wants "just a small model call" during ingest.
- **IMP-005**: OCR, when added, remains within this boundary: Tesseract or EasyOCR are
  deterministic and do not violate the rule.

## References

- **REF-001**: `docs/product-brief.md` PRIN-002 — the principle this ADR implements
- **REF-002**: `docs/architecture.md` BND-001 — the structural enforcement
- **REF-003**: [ADR-0005](adr-0005-fts5-before-vectors.md) — retrieval over these chunks
- **REF-004**: [ADR-0006](adr-0006-llm-gateway.md) — where models *are* used
