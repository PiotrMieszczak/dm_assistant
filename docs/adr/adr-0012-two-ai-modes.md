---
title: "ADR-0012: Two AI modes — Research and Creative — plus in-character roleplay"
status: "Accepted"
date: "2026-09-06"
authors: "Piotr Mieszczak"
tags: ["architecture", "decision", "assistant", "product", "grounding"]
supersedes: ""
superseded_by: ""
---

# ADR-0012: Two AI modes — Research and Creative — plus in-character roleplay

## Status

Proposed | **Accepted** | Rejected | Superseded | Deprecated

## Context

The product brief states a non-goal: *"Not a content generator at the core. Generation is a
convenience, not the thesis."* The intended product contradicts it. A game master needs
help **creating** a campaign — adventures, NPCs and their characteristics, factions,
regions, dialogue — not only looking things up in it.

That collides with `PRIN-001`, which says the assistant answers from indexed material and
refuses when material does not cover a question. Grounding is the reason answers are
trustworthy. But an assistant that refuses to invent cannot help write an adventure, and an
assistant that invents freely cannot be trusted on a rules question.

The failure this must avoid is specific: **a GM who cannot tell whether "the Pale Court
seeks the vault cipher" came from their own notes or was improvised.** Once invention and
retrieval are indistinguishable, an invention eventually gets treated as canon.

Constraints:

- **CON-001**: Both behaviours are wanted. Grounded lookup and creative generation are each
  first-class, not one serving the other.
- **CON-002**: They are mutually exclusive in a single response. "Answer only from sources"
  and "invent something good" cannot both govern the same output.
- **CON-003**: The distinction must be **visible**, not a matter of the GM reading
  carefully. Careful reading fails mid-session.
- **CON-004**: The design specifies one AI panel, 400px wide, present on every workspace
  screen. It is built for quick lookups beside other work.
- **CON-005**: Roleplaying an NPC is a third behaviour again — invention constrained to one
  character's voice, where the speaker's identity matters more than the content's
  provenance.
- **CON-006**: Creative output must fit the world. A new NPC that ignores existing factions
  creates reconciliation work rather than saving it.

## Decision

**Three modes, each with its own rule about invention, each visually distinct.**

### 1. Research — the side panel

The mode the design already draws, in the 400px panel, available on every screen.

Behaves like NotebookLM: **answers only from indexed sources, cites them, and says plainly
when the sources do not cover the question.** This is `PRIN-001` unchanged.

Used *while* doing something else — a rules question mid-session, "what did we establish
about Doran Vey", "summarise last session".

### 2. Creative — its own page

A full page, not the panel. Creation is the activity, not something done beside another
activity: it needs room for long output, iteration, and saving results into the campaign.

**Invention is the point.** The model drafts adventures, NPCs, factions, regions, and
dialogue.

**Campaign-aware.** Existing entities and session history are supplied as context so new
content fits the world — a new NPC can reference the Pale Court coherently (CON-006).
Context informs; it does not constrain the way sources constrain Research mode.

**Everything it produces is labelled as invention** and reaches the campaign only through
the proposal flow ([ADR-0011](adr-0011-assistant-tools.md)): a draft the GM edits and
confirms.

### 3. In character — entered from a character

Opened from a character's page ("Speak as Doran Vey"). The panel becomes that character:
their portrait and name replace the assistant header, so who is talking is never ambiguous.

Their sheet, notes, and relationships are context, so the voice stays consistent. The model
improvises freely within it.

**Nothing said in character is canon** unless the GM explicitly saves it to the character's
notes or a session record.

### A mode is a bundle, not just a prompt

Each mode is a **profile**: prompt, sampling parameters, tool set, and model preference.
Prompting alone does not make grounding reliable — a model at high temperature will
embellish despite being told not to.

| | Research | Creative | In character |
|---|---|---|---|
| **Invention** | Never | The point | Within one voice |
| **Temperature** | **0** | 0.8–1.0 | 0.7–0.9 |
| **Tools** | `search_documents`, `get_*` | `get_*`, `propose_*` | `get_character` only |
| **Model** | Cheaper is fine | Prefer the stronger one | Either |
| **Where** | Side panel | Its own page | Panel, restyled as the NPC |
| **Output reaches campaign data** | No — answers only | Via proposal + confirm | Only if explicitly saved |

**Temperature 0 in Research mode is load-bearing.** It makes answers near-deterministic —
the same question against the same sources gives the same answer — which is what makes
citations verifiable and refusals consistent rather than occasional. A grounding prompt at
temperature 0.8 is a suggestion; at 0 it is close to a constraint.

**Creative mode wants the opposite.** Low temperature produces the obvious idea, which is
the one the GM already had. Variety is the value.

**`PRIN-001` is scoped, not weakened.** It stops being a product-wide rule and becomes the
defining rule of Research mode. That is a stronger position than before: previously
"never invent" was stated globally and would have been quietly violated the first time
someone asked for an adventure.

## Consequences

### Positive

- **POS-001**: The product can do what a GM actually needs — create *and* consult — without
  either behaviour compromising the other.
- **POS-002**: Provenance is structural (CON-003). The GM is in one mode or another, and
  the interface says which. No inference required.
- **POS-003**: Research mode's guarantee gets *stronger*. With creation handled elsewhere,
  there is no pressure to soften "refuse when unsupported" — the pressure that would have
  eroded it.
- **POS-004**: Creative mode gets a surface suited to it, rather than long drafts squeezed
  into a 400px panel (CON-004).
- **POS-005**: Roleplay entered from a character makes the speaker unambiguous and gives
  the model the right context automatically.
- **POS-006**: The proposal rule ([ADR-0011](adr-0011-assistant-tools.md)) already covers
  creative output reaching the database, so no new write path is introduced.

### Negative

- **NEG-001**: A whole page the design does not specify. Creative mode has no screen,
  no layout, no interaction spec — the largest design gap yet.
- **NEG-002**: Three modes is more product surface: three prompt strategies, three sets of
  context assembly, three things to test.
- **NEG-003**: Mode confusion is now the failure to guard against. If the visual distinction
  is weak, the whole safety argument collapses to careful reading, which CON-003 rejects.
- **NEG-004**: Creative quality has no metric. Retrieval has an eval set; "is this a good
  adventure hook?" does not, and probably cannot in the same way.
- **NEG-005**: Campaign-aware creation means assembling context from several entity types,
  which is more work than Research's chunk retrieval and easier to get wrong.
- **NEG-006**: Scope grew again. Creative mode plus roleplay is a substantial addition to a
  v1 that had not yet proven retrieval.

### Neutral

- **NOTE-001**: The product brief's non-goal — *"not a content generator at the core"* —
  is now false and is replaced. Recorded here so the change is deliberate rather than
  drifted into.

## Alternatives Considered

### One assistant that switches tone on request

- **ALT-001**: **Description**: A single chat where the model answers from sources normally
  and invents when asked to.
- **ALT-002**: **Rejection Reason**: Fails CON-003 exactly. The GM must track which mode
  the last response came from, mid-session, under time pressure. This is the failure the
  ADR exists to prevent, and it is the most likely way to build the feature by accident.

### Both modes in the side panel, with a toggle

- **ALT-003**: **Description**: One control switches the existing panel between grounded and
  creative behaviour.
- **ALT-004**: **Rejection Reason**: Better than ALT-001 — the mode is at least explicit —
  but a toggle is easy to lose track of, and 400px is a poor surface for drafting an
  adventure (CON-004). Rejected on fit rather than principle.

### Keep generation out of the product

- **ALT-005**: **Description**: Honour the existing non-goal. The assistant retrieves;
  the GM writes.
- **ALT-006**: **Rejection Reason**: Contradicts CON-001 and what the product is for.
  Creation is most of a game master's work.

### Roleplay inside Creative mode

- **ALT-007**: **Description**: Ask the creative assistant to play a character rather than
  having a separate mode.
- **ALT-008**: **Rejection Reason**: Fewer concepts, but it loses the thing that makes
  roleplay work — an unambiguous speaker and automatic character context (CON-005). "Who is
  talking" becomes a prompt detail rather than a visible state.

## Implementation Notes

- **IMP-001**: The Gateway ([ADR-0006](adr-0006-llm-gateway.md)) holds **three mode
  profiles**, not one prompt. A profile is prompt + temperature + tool set + model
  preference, defined in exactly one place and selected by mode.
- **IMP-001a**: Research mode runs at **temperature 0**. This is not a tuning preference —
  it is what makes AC-003's refusal behaviour consistent rather than probabilistic. Test
  refusal at the temperature that ships.
- **IMP-002**: Research mode's prompt is unchanged and remains the strictest: answer only
  from context, state plainly when context is insufficient.
- **IMP-003**: Creative mode's prompt states that output is a draft for a game master,
  should fit the supplied campaign context, and is **not** presented as fact.
- **IMP-004**: In-character prompts carry the character's sheet, notes, relationships, and
  quote. Include the instruction that the character does not know things the character
  would not know.
- **IMP-005**: **Make the mode unmissable** (NEG-003). Distinct accent treatment per mode,
  the mode named in the panel or page header, and in-character mode showing the NPC's
  portrait and name rather than the assistant's. This is the safety mechanism, not
  decoration.
- **IMP-006**: Creative and in-character output must never be indexed as source material.
  Only documents and session records the GM has saved enter the index — otherwise
  invention becomes retrievable as fact, which defeats
  [ADR-0002](adr-0002-deterministic-extraction.md) from the other direction. Add a test.
- **IMP-007**: Conversations record their mode. A message's provenance must be readable
  later, not only while it is on screen.
- **IMP-008**: Creative mode is campaign-aware but context has a budget. Assemble a summary
  of relevant entities, not every row — see `rag-evaluation` on why more context is not
  better context.
- **IMP-009**: Creative mode needs design before implementation (NEG-001). It is a page,
  and the design specifies none.

## References

- **REF-001**: [ADR-0011](adr-0011-assistant-tools.md) — the proposal flow creative output
  uses to reach the campaign
- **REF-002**: [ADR-0002](adr-0002-deterministic-extraction.md) — the index boundary
  IMP-006 protects from the other side
- **REF-003**: [ADR-0006](adr-0006-llm-gateway.md) — the Gateway, which now owns three
  prompt strategies
- **REF-004**: `docs/product-brief.md` PRIN-001 — scoped by this record to Research mode
- **REF-005**: [NotebookLM](https://notebooklm.google/) — the reference for what Research
  mode should feel like
