# Product Brief

## One line

An in-session workspace for tabletop RPG game masters: campaign material on the left,
an assistant grounded in that material on the right.

## The problem

Running a session means holding too much in your head at once. A GM juggles a rulebook,
an adventure module, their own notes, a cast of NPCs, faction politics, and a quest log —
while improvising in real time in front of players. The failure mode is not *lack of
information*; it is **retrieval latency**. The answer is in the PDF. Finding it takes
ninety seconds, and the table is waiting.

Existing tools solve half of it. Note apps store material but cannot answer questions
about it. Generic AI chat answers questions but invents rules that are not in *your*
books, which is worse than useless at the table.

## The product

DM Assistant keeps campaign material indexed and puts an assistant next to it that
answers **only** from what has been indexed. The GM asks in natural language; the answer
is grounded in their own documents, with the source visible.

Around that core sits the session-running workspace the design defines: NPCs, players,
factions, a quest log, session records, and a knowledge graph of how everyone relates.

### Who it is for

Game masters running live sessions, primarily at a table or over video, for systems like
D&D 2024 and Traveller 2e. Single-user, local-first. Not a player-facing tool, not a
virtual tabletop, not a campaign-sharing platform.

### The core loop

1. **Prepare** — upload rulebooks, modules, and notes; they are extracted and indexed.
2. **Populate** — record NPCs, players, factions, and quests for the campaign.
3. **Run** — during a session, ask the assistant, consult the graph, update quest state.
4. **Record** — write a session log; it becomes searchable material for next time.

## Product principles

**PRIN-001 — Grounded, never inventive about facts.**
The assistant answers from indexed material. When material does not cover a question, it
says so rather than filling the gap. Creative help (drafting a scene, voicing an NPC) is
clearly distinct from factual retrieval.

**PRIN-002 — Extraction is deterministic.**
Text extraction and parsing use libraries, not language models. This keeps ingestion
testable against fixtures, cheap, and reproducible. AI acts only on already-indexed data.
See [adr/adr-0002-deterministic-extraction.md](adr/adr-0002-deterministic-extraction.md).

**PRIN-003 — The session is the priority.**
The workspace is used live, with players waiting. Interactions target under 300ms.
Nothing blocks the GM mid-session; long work (document processing) happens in the
background with visible status.

**PRIN-004 — Local-first, single-user.**
Data lives on the GM's machine. No accounts to manage, no sync, no sharing in v1. The
login screen exists in the design as a shell for later multi-user work; v1 treats it as
a local profile.

**PRIN-005 — The interface is calm.**
Dark, low-chrome, image-forward. The tool sits beside a game; it should not compete with
it for attention.

## What success looks like

The MVP is successful if a GM can:

1. Upload a rulebook and see it reach `Indexed` status without intervention.
2. Ask a rules question mid-session and get a correct answer grounded in that book,
   fast enough not to stall the table.
3. Keep their campaign's NPCs, factions, and quests in the workspace instead of scattered
   notes, and find them faster than before.

If retrieval is not trustworthy, nothing else in the product matters — every other
feature assumes the GM believes the answers.

## Explicit non-goals

- **Not a virtual tabletop.** No maps, tokens, initiative tracking, or dice rolling.
- **Not player-facing.** No player logins, no shared views, no handouts.
- **Not a rules engine.** It retrieves and explains rules; it does not adjudicate them.
- **Not a content generator at the core.** Generation is a convenience, not the thesis.
- **Not multi-tenant.** No hosting, no organisations, no collaboration in v1.
