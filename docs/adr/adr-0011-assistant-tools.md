---
title: "ADR-0011: Assistant tools, and writes go through a proposal"
status: "Accepted"
date: "2026-09-06"
authors: "Piotr Mieszczak"
tags: ["architecture", "decision", "assistant", "tools", "llm", "safety"]
supersedes: "ADR-0010"
superseded_by: ""
---

# ADR-0011: Assistant tools, and writes go through a proposal

## Status

Proposed | **Accepted** | Rejected | Superseded | Deprecated

## Context

[ADR-0010](adr-0010-no-agent-framework.md) reasoned from a narrow premise: one assistant,
one read-only tool, no loop. Real usage is broader. A game master will ask things like:

- *"What are the rules for opportunity attacks?"* — retrieve and answer
- *"Summarise last session"* — fetch a record and transform it
- *"Analyse this module and create an NPC from it"* — extract structured data and **write**

The third is a different shape. It needs several tool calls whose results feed the next
decision, and it ends by creating a row in the campaign. That is a real multi-step loop and
a write, neither of which ADR-0010 accounted for.

It also sits close to a line already drawn.
[ADR-0002](adr-0002-deterministic-extraction.md) forbids language models in the ingestion
path so that the index contains only text genuinely present in the source. "Create an NPC
from this PDF" is asking a model to extract structured data from a document, which looks
like the forbidden thing.

Constraints:

- **CON-001**: The assistant needs at least three request shapes: retrieve-and-answer,
  fetch-and-transform, and extract-and-propose.
- **CON-002**: Extraction is inherently lossy and occasionally wrong. A model reading a
  module will sometimes invent a stat or misattribute a relationship.
- **CON-003**: A wrong answer is recoverable — the GM reads it and disagrees. A wrong
  **write** persists silently and is discovered later, possibly mid-session.
- **CON-004**: ADR-0002 must not be quietly eroded. Whatever is built has to be
  distinguishable from "an LLM builds the index."
- **CON-005**: The project is a learning exercise ([ADR-0008](adr-0008-own-auth-v1.md)).
  A tool loop is one of the things worth understanding directly.
- **CON-006**: Tool calls are visible in the design — the AI panel has green check chips
  showing what ran.

## Decision

**Three tool shapes, and every write goes through a proposal the GM confirms.**

### Tools

| Tool | Reads | Writes | Shape |
|------|-------|--------|-------|
| `search_documents` | Indexed chunks | — | retrieve |
| `get_session` / `list_sessions` | Session records | — | fetch |
| `get_character` / `get_faction` | Campaign entities | — | fetch |
| `propose_character` | — | **Draft only** | propose |
| `propose_faction` | — | **Draft only** | propose |

### The proposal rule

**No tool writes to the campaign.** `propose_character` does not insert a row. It returns a
populated draft — fields, plus the chunk ids each field was drawn from — which the frontend
renders as a pre-filled form inside the chat. The GM edits what is wrong and clicks create.
The ordinary `POST /characters` endpoint does the write, exactly as if it had been typed.

The model can *suggest*. Only the GM *commits*.

### Why this does not violate ADR-0002

The distinction is precise and worth stating, because the two look similar:

| | ADR-0002 forbids | This ADR permits |
|---|---|---|
| **What is read** | Raw document bytes | Already-indexed chunks |
| **What is produced** | The searchable index | A draft for review |
| **When** | Automatically, on every upload | Only on explicit request |
| **Persisted without review?** | Would be | **No** |
| **If wrong** | Silently corrupts all retrieval | Visible in a form, corrected before saving |

Ingestion remains deterministic. This operates *downstream* of the index, on text already
proven to exist, and its output is a suggestion rather than a record.

### Still no framework

The conclusion of ADR-0010 survives the wider scope. Three or four tools in one loop is not
framework territory: the loop is a bounded `while` over tool calls, and the alternative
would take ownership of prompt assembly, which
[ADR-0006](adr-0006-llm-gateway.md) reserves. Reassess at real branching or sub-agents, and
reassess Pydantic AI first.

## Consequences

### Positive

- **POS-001**: The assistant becomes useful for the work a GM actually does, not only rules
  lookup.
- **POS-002**: A model can never silently change campaign data (CON-003). The worst failure
  is a bad draft, which is visible and free to discard.
- **POS-003**: Proposals carry the chunk ids each field came from, so the GM sees *why* a
  field was filled in — the same grounding discipline as answers (AC-002).
- **POS-004**: ADR-0002 stays intact and, by being distinguished explicitly here, becomes
  harder to erode by accident (CON-004).
- **POS-005**: The tool loop is written by hand, which is the learning value under CON-005.
- **POS-006**: The design's tool-call chips gain real content — "Searched 3 documents",
  "Drafted Brother Cael" (CON-006).

### Negative

- **NEG-001**: More tools means more surface. Each needs a schema, a description the model
  can act on, and tests.
- **NEG-002**: The loop must be bounded. An unbounded tool loop is a runaway bill, and with
  several tools the model has more ways to spin.
- **NEG-003**: The proposal flow needs UI the design does not specify — a draft entity form
  rendered inside a chat bubble. Another entry on the design-gap list.
- **NEG-004**: Extraction quality is unmeasured. Unlike retrieval, which has an eval set,
  "is this NPC well extracted?" has no metric yet.
- **NEG-005**: The distinction from ADR-0002 is a judgement, not a mechanism. Nothing
  structurally prevents someone later wiring a proposal tool into the upload path.
- **NEG-006**: Two supersessions of the framework question in one project. The answer has
  held both times, but a third scope increase may not leave it standing.

## Alternatives Considered

### Write directly, allow undo

- **ALT-001**: **Description**: `create_character` inserts immediately; the entity appears
  flagged as AI-generated and the GM can delete it.
- **ALT-002**: **Rejection Reason**: Fails CON-003. Undo assumes the error is noticed, and
  the likely failure is not a wholly invented NPC but a mostly-right one with a wrong stat
  or a misattributed faction — precisely what is not noticed until it matters. A flag marks
  provenance, not correctness.

### Read-only assistant

- **ALT-003**: **Description**: The assistant answers and summarises but creates nothing;
  it can print an NPC as text to copy in by hand.
- **ALT-004**: **Rejection Reason**: Safest, and it forgoes most of the value. Copying
  fields by hand from a chat bubble is the tedium the feature exists to remove. The
  proposal flow gets the same safety from confirmation rather than from refusal.

### Automatic entity extraction on upload

- **ALT-005**: **Description**: Extract NPCs from every document as it is indexed, so a
  campaign is populated without asking.
- **ALT-006**: **Rejection Reason**: This *is* the thing ADR-0002 forbids — a model in the
  ingestion path, writing unreviewed. It also fails CON-002 at scale: a hundred silently
  created NPCs of uncertain quality is worse than none. Already deferred in
  `mvp-scope.md`, and this ADR does not revive it.

### Adopt Pydantic AI for the tool loop

- **ALT-007**: **Description**: Use a typed framework for tool definitions, the loop, and
  structured extraction output.
- **ALT-008**: **Rejection Reason**: The best-fitting framework, and structured extraction
  is where it would earn most. Deferred on CON-005 for now, with the trigger unchanged from
  ADR-0010: real branching or sub-agents. Reassess this first, not LangChain.

## Implementation Notes

- **IMP-001**: Every tool declares a JSON schema and a description written for a reader who
  cannot see the code. `"limit"` teaches the model nothing; `"maximum results, default 5"`
  tells it when to set the field.
- **IMP-002**: **Cap the loop.** Five to ten iterations, then stop with an explicit error.
  Non-negotiable (NEG-002).
- **IMP-003**: `propose_*` tools return a draft object plus `sources: [chunk_id]` per
  populated field. A field with no source is a field the model invented — surface it as
  such in the form.
- **IMP-004**: Proposals are **never** persisted, not even as a draft row. They live in the
  message payload until the GM submits the normal create endpoint.
- **IMP-005**: The write path stays the existing `POST /characters`, with the same
  validation and the same owner scoping (`BND-003`). No privileged assistant write path
  exists to be exploited.
- **IMP-006**: Tool calls emit AG-UI `ToolCallStart` / `ToolCallResult`
  ([ADR-0009](adr-0009-ag-ui-protocol.md)), which drive the design's check chips.
- **IMP-007**: Add an architectural test asserting no `propose_*` tool is reachable from
  `ingestion/`. That converts NEG-005 from a convention into a boundary, matching how
  BND-001 is enforced.
- **IMP-008**: Build an extraction eval set alongside the retrieval one — fixture documents
  with expected entities. Without it, NEG-004 stands and extraction quality is a guess.

## References

- **REF-001**: [ADR-0010](adr-0010-no-agent-framework.md) — superseded; its conclusion
  survives, its premise did not
- **REF-002**: [ADR-0002](adr-0002-deterministic-extraction.md) — the ingestion boundary
  this is careful not to cross
- **REF-003**: [ADR-0006](adr-0006-llm-gateway.md) — the Gateway, which still owns the
  grounding prompt
- **REF-004**: [ADR-0009](adr-0009-ag-ui-protocol.md) — the events tool calls emit
- **REF-005**: `docs/product-brief.md` PRIN-001 — grounding, which proposals extend by
  citing sources per field
