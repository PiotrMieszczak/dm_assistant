---
title: "ADR-0010: No agent framework; own the assistant loop"
status: "Accepted"
date: "2026-09-02"
authors: "Piotr Mieszczak"
tags: ["architecture", "decision", "assistant", "llm", "learning"]
supersedes: ""
superseded_by: ""
---

# ADR-0010: No agent framework; own the assistant loop

## Status

Proposed | **Accepted** | Rejected | Superseded | Deprecated

## Context

The assistant answers a question by retrieving chunks, prompting a model with them as
context, and streaming the reply. That loop — receive, retrieve, prompt, stream, cite — has
to live somewhere.

Agent frameworks exist to own exactly this. LangChain and LangGraph are the best known;
Pydantic AI, CrewAI, and Mastra occupy the same space. Several list
[AG-UI](https://docs.ag-ui.com/introduction) integrations, which makes them a natural
question once AG-UI is adopted ([ADR-0009](adr-0009-ag-ui-protocol.md)).

Constraints:

- **CON-001**: The project is a learning exercise as much as a tool
  ([ADR-0008](adr-0008-own-auth-v1.md)). A framework that runs the loop hides the loop.
- **CON-002**: The MVP has **one** assistant with **one** tool (search the campaign's
  indexed chunks). No sub-agents, no branching, no multi-step planning.
- **CON-003**: [ADR-0006](adr-0006-llm-gateway.md) already establishes a Gateway that owns
  provider access and, critically, the **grounding prompt** — the instruction to answer
  only from supplied context and to say so when it is absent (PRIN-001, AC-003).
- **CON-004**: AG-UI is a wire protocol, not a framework. It does not require LangChain or
  any other library; conforming events can be emitted from plain FastAPI code.
- **CON-005**: Frameworks move fast and break. A dependency that owns the core loop is a
  dependency whose upgrades are never optional.

## Decision

**No agent framework.** The assistant loop is plain Python in FastAPI:

```
receive message
  → retrieve chunks (FTS5)
  → assemble context + citations
  → Gateway.stream(grounding_prompt, context, question)
  → emit AG-UI events as tokens arrive
```

The Gateway ([ADR-0006](adr-0006-llm-gateway.md)) remains the only place a provider SDK is
imported and the only place the grounding prompt is constructed. AG-UI events are emitted
directly from the endpoint.

No LangChain, no LangGraph, no Pydantic AI, no CrewAI.

## Consequences

### Positive

- **POS-001**: Every step of the loop is visible in the repository's own code, which is the
  learning value under CON-001. Nothing about how a question becomes a grounded answer is
  behind an abstraction.
- **POS-002**: The grounding prompt stays in one place under direct control. A framework
  that assembles prompts from chains and templates would scatter the rule that PRIN-001
  depends on — the failure [ADR-0006](adr-0006-llm-gateway.md) exists to prevent.
- **POS-003**: Far fewer dependencies. LangChain pulls a large transitive tree for a loop
  that is a few dozen lines here.
- **POS-004**: Debugging is direct. A wrong answer is traced by reading the retrieval call
  and the prompt, not by instrumenting a framework's internals.
- **POS-005**: No framework upgrade treadmill (CON-005).
- **POS-006**: AG-UI conformance is unaffected — the protocol is the contract, and
  emitting it from plain code is exactly as valid (CON-004).

### Negative

- **NEG-001**: Anything a framework would provide must be built if it is ever needed:
  multi-step tool loops, conversation memory beyond message history, retry and fallback
  policies, structured output parsing.
- **NEG-002**: No exposure to a widely-used ecosystem. LangChain literacy is genuinely
  useful to have, and this decision forgoes it in this project.
- **NEG-003**: Framework-adjacent tooling — LangSmith tracing, prebuilt evaluators — is
  unavailable without building equivalents.
- **NEG-004**: If the product later wants several cooperating agents, this loop is not the
  foundation for that and would be rewritten rather than extended.

## Alternatives Considered

### LangChain or LangGraph

- **ALT-001**: **Description**: The dominant agent framework. Chains, tool-calling loops,
  memory, retrievers, and a first-party AG-UI integration.
- **ALT-002**: **Rejection Reason**: It takes over the loop and, with it, prompt assembly —
  putting the grounding rule inside a framework abstraction rather than in one place we
  control (CON-003). That is a direct conflict with ADR-0006, not a stylistic preference.
  Its value is orchestrating complexity this product does not have (CON-002), and under
  CON-001 the loop is the thing worth understanding. LangGraph specifically solves
  branching and state machines across steps — there is one step.

### Pydantic AI

- **ALT-003**: **Description**: A lighter, typed, Python-native agent framework, also with
  AG-UI support.
- **ALT-004**: **Rejection Reason**: A genuinely better fit than LangChain — less
  abstraction, and its typed tool definitions are close to what would be hand-written
  anyway. Rejected on the same CON-001 grounds rather than on merit: it still owns the
  loop. **This is the first alternative to revisit** if hand-rolling becomes tedious rather
  than instructive.

### A framework for tool-calling only, with our own prompt

- **ALT-005**: **Description**: Use a framework's tool-calling loop while keeping the
  grounding prompt in the Gateway.
- **ALT-006**: **Rejection Reason**: Splits ownership of the loop in a way that is harder
  to reason about than either extreme. With one tool, the loop being delegated is roughly
  twenty lines.

## Implementation Notes

- **IMP-001**: The loop lives in `backend/app/api/assistant.py`. Keep it readable top to
  bottom — it is the file that explains how the product works.
- **IMP-002**: Retrieval stays behind the interface in `app/retrieval/`
  ([ADR-0005](adr-0005-fts5-before-vectors.md)) so the loop does not know how search is
  implemented.
- **IMP-003**: The grounding prompt is built in `app/gateway/` and nowhere else
  ([ADR-0006](adr-0006-llm-gateway.md) IMP-002). The loop passes context; it does not
  assemble instructions.
- **IMP-004**: Cap tool iterations explicitly even with one tool. An unbounded loop is a
  runaway bill, and the cap is one line now versus a bug later.
- **IMP-005**: If a second tool appears, add it to the same loop before reaching for a
  framework. Two tools is not complexity; five with branching is.
- **IMP-006**: Revisit trigger — multi-step planning, sub-agents, or a tool loop that needs
  real branching. Reassess Pydantic AI first (ALT-003), not LangChain.

## References

- **REF-001**: [ADR-0006](adr-0006-llm-gateway.md) — the Gateway, which owns provider
  access and the grounding prompt
- **REF-002**: [ADR-0009](adr-0009-ag-ui-protocol.md) — AG-UI, which this loop emits
- **REF-003**: [ADR-0008](adr-0008-own-auth-v1.md) — the same reasoning applied to
  authentication
- **REF-004**: `docs/product-brief.md` PRIN-001 — grounding, the rule the prompt enforces
