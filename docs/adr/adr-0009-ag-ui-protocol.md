---
title: "ADR-0009: AG-UI protocol for assistant streaming"
status: "Accepted"
date: "2026-09-02"
authors: "Piotr Mieszczak"
tags: ["architecture", "decision", "protocol", "streaming", "assistant"]
supersedes: ""
superseded_by: ""
---

# ADR-0009: AG-UI protocol for assistant streaming

## Status

Proposed | **Accepted** | Rejected | Superseded | Deprecated

## Context

The assistant streams its answer to the browser: tokens as they are generated, an
indicator of which tools ran, and the citations backing each claim.

`api-contract.md` originally specified a hand-written SSE contract — four event names
(`token`, `tool`, `citation`, `done`, `error`) invented for this project. It works, and it
is small.

[AG-UI](https://docs.ag-ui.com/introduction) is an open, event-based protocol for exactly
this problem: connecting an agentic backend to a user-facing application. It defines typed
lifecycle, message, tool-call, and state events, and it is supported by LangChain, CrewAI,
Pydantic AI, Mastra, and others.

Constraints:

- **CON-001**: The project is a learning exercise as much as a tool
  ([ADR-0008](adr-0008-own-auth-v1.md)). Implementing a real specification teaches more
  than inventing four event names.
- **CON-002**: The MVP has **one** assistant, one-directional streaming, and no agent
  composition. Most of AG-UI's surface — sub-agents, agent steering, generative UI — is
  out of scope.
- **CON-003**: The hand-rolled contract already mirrors AG-UI's streaming subset. The two
  converged independently, which is evidence the shape is right rather than a reason to
  keep the private version.
- **CON-004**: Grounding with citations is this product's defining behaviour (PRIN-001,
  AC-002). Whatever protocol is used must carry citations.
- **CON-005**: There is no Python server SDK listed among AG-UI's official SDKs; the
  backend is FastAPI ([ADR-0001](adr-0001-react-vite-spa.md)). The event schema is the
  contract, and emitting conforming events does not require an SDK.

## Decision

**The assistant's streaming endpoint speaks AG-UI**, replacing the hand-written event
names.

Mapping from the previous contract:

| Was | Becomes |
|-----|---------|
| `token` | `TextMessageStart` → `TextMessageContent` (delta) → `TextMessageEnd` |
| `tool` | `ToolCallStart` → `ToolCallArgs` → `ToolCallEnd` → `ToolCallResult` |
| `done` | `RunFinished` |
| `error` | `RunError` |
| `citation` | **`Custom`** — see below |

**Citations use a custom event.** AG-UI has no citation type, because grounding is a
product concern rather than a protocol one. Rather than bending `ToolCallResult` into
carrying them, citations are emitted as a namespaced custom event
(`dm.citation`) with the chunk id, document, and page span. The protocol explicitly
provides for this, and it keeps the product-specific part clearly marked as product-specific.

Adopted **now**, in the MVP, rather than deferred. The cost of changing the transport later
is higher than the cost of using it from the start, and under CON-001 the implementation
is itself the point.

**Not adopted:** sub-agent composition, agent steering, generative UI, and shared-state
sync. Those parts of AG-UI stay unused until something needs them.

## Consequences

### Positive

- **POS-001**: A real, documented specification is implemented rather than a private one
  invented per project — the learning value under CON-001.
- **POS-002**: The event contract is typed on both ends. The frontend consumes
  `@ag-ui/core` types instead of hand-written interfaces that can drift from the server.
- **POS-003**: `api-contract.md` no longer has to define an event schema; it references
  the protocol and documents only what is product-specific.
- **POS-004**: The lifecycle events (`RunStarted`, `RunFinished`, `RunError`) make run
  boundaries explicit. The hand-rolled contract had `done` but no start, so the client
  could not distinguish "not begun" from "begun but silent".
- **POS-005**: Interrupts, agent steering, and multi-agent composition become available
  without redesigning the transport if they are ever wanted.
- **POS-006**: Tool calls gain a proper lifecycle. The previous `tool` event was a single
  label; AG-UI distinguishes invocation, arguments, and result, which the design's green
  check chips can reflect more honestly.

### Negative

- **NEG-001**: More events than the MVP needs. A single token now involves three event
  types where one sufficed.
- **NEG-002**: No official Python server SDK, so the backend emits conforming events by
  hand. The schema is the contract, but there is no library validating conformance.
- **NEG-003**: An external specification can change. A private contract changes only when
  we change it.
- **NEG-004**: Citations sit outside the standard event set, so that part is bespoke
  regardless — the protocol does not remove product-specific work.
- **NEG-005**: A reader must learn AG-UI to follow the streaming code, where four
  invented event names were self-explanatory.
- **NEG-006**: The protocol is young. Adoption is a bet that it stays maintained.

## Alternatives Considered

### Keep the hand-rolled SSE contract

- **ALT-001**: **Description**: Five invented event names over plain SSE, as originally
  specified in `api-contract.md`.
- **ALT-002**: **Rejection Reason**: Adequate and simpler, but it is a private
  reimplementation of AG-UI's streaming subset (CON-003) with none of the learning value
  (CON-001) and no path to interrupts or composition. The convergence is the argument
  against it: if the shape is already AG-UI's, use AG-UI's.

### Adopt AG-UI later, when a second agent appears

- **ALT-003**: **Description**: Ship the hand-rolled version, adopt the protocol when
  multi-agent or steering is actually needed.
- **ALT-004**: **Rejection Reason**: Defensible sequencing, and it is the pattern used for
  the vector store ([ADR-0005](adr-0005-fts5-before-vectors.md)). Rejected here because
  the trigger differs: a vector store is deferred pending *evidence* that keyword search
  fails, while AG-UI's value under CON-001 exists immediately. Changing the transport later
  also touches both ends at once, unlike swapping a retrieval implementation behind an
  interface.

### CopilotKit

- **ALT-005**: **Description**: A frontend framework that speaks AG-UI and supplies
  ready-made chat components.
- **ALT-006**: **Rejection Reason**: The design specifies a fully custom AI panel — its
  own bubbles, tool chips, streaming cursor, and composer. Prebuilt components would be
  fought rather than used. The protocol is adopted; the component library is not.

### WebSockets instead of SSE

- **ALT-007**: **Description**: A bidirectional transport, since AG-UI supports agent
  steering.
- **ALT-008**: **Rejection Reason**: The MVP streams one direction. AG-UI is transport
  agnostic, so SSE now does not foreclose WebSockets later. See
  `docs/architecture.md` for why SSE fits a request-with-streamed-reply shape.

## Implementation Notes

- **IMP-001**: The backend emits AG-UI events from `app/api/assistant.py`. Model-provider
  streams are normalised into AG-UI events inside the Gateway boundary
  ([ADR-0006](adr-0006-llm-gateway.md)), so provider differences never reach the wire.
- **IMP-002**: The frontend consumes `@ag-ui/core` types. Do not hand-write event
  interfaces; that reintroduces the drift the protocol removes.
- **IMP-003**: Custom events are namespaced (`dm.citation`) so product-specific events are
  visibly distinct from protocol events.
- **IMP-004**: Emit `RunStarted` before any work, and exactly one of `RunFinished` or
  `RunError` to close. A stream that ends without either is a bug — the client cannot
  distinguish it from a dropped connection.
- **IMP-005**: Cancellation still propagates as described in the streaming design: client
  aborts, `CancelledError` reaches the generator, the provider stream closes. Do not
  swallow it, or the provider call keeps running and billing.
- **IMP-006**: Test the failure paths explicitly — error after partial output,
  cancellation mid-stream, and a provider returning nothing. These are where streaming
  breaks and none appear in a happy-path test.
- **IMP-007**: Since there is no Python SDK (NEG-002), add a test asserting emitted events
  match the documented AG-UI schema. Without it, conformance is assumed rather than checked.
- **IMP-008**: Revisit trigger — if AG-UI becomes unmaintained, or its complexity exceeds
  its value for a single agent, the mapping table above makes reverting to a private
  contract mechanical.

## References

- **REF-001**: [AG-UI introduction](https://docs.ag-ui.com/introduction)
- **REF-002**: [AG-UI event types](https://docs.ag-ui.com/concepts/events)
- **REF-003**: [ADR-0006](adr-0006-llm-gateway.md) — the Gateway, which normalises provider
  streams into these events
- **REF-004**: `docs/api-contract.md` — the assistant endpoint
- **REF-005**: `docs/product-brief.md` PRIN-001 — grounding, which the citation event serves
