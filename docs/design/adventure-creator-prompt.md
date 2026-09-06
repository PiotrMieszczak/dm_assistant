# Design prompt — Adventure Creator page

A brief for [Claude Design](https://claude.ai/design) to produce the Creative mode page,
which the current design does not specify ([ADR-0012](../adr/adr-0012-two-ai-modes.md)).

**How to use it:** paste the block below into Claude Design in the same project as
*RPG Assistant Design Spec*, so it inherits the existing tokens and shell.

**What it must produce:** a page that closes design gaps 6 and 7 in
[mvp-scope.md](../mvp-scope.md), and renders the Adventure model in
[data-model.md](../data-model.md).

---

## The prompt

````
Design an "Adventure Creator" page for Referee, the tabletop RPG game master
workspace in this project. Match the existing dark aesthetic, tokens, and shell
exactly — this is a new page inside the app already designed here, not a new product.

## Context

Referee has two AI modes that must never be confused with each other:

- RESEARCH lives in the 400px side panel already designed. It answers ONLY from the
  GM's indexed rulebooks and notes, cites sources, and refuses when the sources do
  not cover a question.
- CREATIVE is this page. It INVENTS. It drafts adventures, NPCs, factions, and
  dialogue, informed by the campaign so new content fits the existing world.

The separation is a safety property, not a layout preference: a game master must
never have to work out whether something came from their books or was invented. So
this page should feel visibly, deliberately different from the Research panel —
while still obviously the same product.

## What the page is for

A GM sits down between sessions to build an adventure. This is authoring, not
lookup: it needs room to write, iterate, and see structure. That is why it is a page
and not the side panel.

## The workflow to support

Experienced GMs prepare in a known order. The page should follow it, so a GM lands in
something that guides them rather than a grid of empty fields:

1. **Review the characters** — what do the players care about right now?
2. **Create a strong start** — the opening scene, with action, roleplay, or mystery
3. **Outline potential scenes** — roughly 1–2 per hour of play
4. **Define secrets and clues** — around 10, NOT tied to any one scene. Any essential
   secret needs at least three different clues pointing at it, because players miss things
5. **Develop interesting locations** — evocative titles, three unique aspects each
6. **Outline important NPCs** — description, one personality quirk, connection to the plot
7. **Choose relevant monsters**
8. **Select rewards** — treasure, information, and hooks into the next adventure

Steps 4 and 5 are where most tools fail. Clues get buried inside scene descriptions, which
is exactly how a party gets stuck.

## Structure to render

An adventure has:
- Title, premise (one paragraph), status (draft / ready / running / completed)
- Level range, expected number of sessions, and the region it happens in
- BACKGROUND — what is really going on. GM-private, never read to players.
- HOOKS — 2 to 4 reasons a party gets involved, each tagged with the motivation it
  appeals to (Duty, Greed, Revenge, Curiosity)
- SCENES — the beats it is made of. Each has a title, a purpose, a summary,
  READ-ALOUD text (spoken at the table), and GM NOTES (private). Scenes can be
  marked optional.
- CLUES — discrete pieces of information, deliberately NOT owned by a scene. A clue
  can surface in several places. Clues that point at an essential secret need at
  least three routes, and the page should show when one has fewer.
- FRONTS — the threats moving in the background: what they want, and a countdown of
  what happens next if nobody stops them. Fronts belong to the campaign and drive
  several adventures, so this is a link, not an edit surface.
- Cast — which NPCs and factions appear, each with a role note

Adventures come in two families, and a GM prepares them very differently:

- PROCEDURAL (dungeon crawl, hexcrawl, point crawl, node-based) — emergent. Needs
  flexible tools: maps, tables, clue lists.
- STORY-DRIVEN (linear, branching, mystery) — directed. Needs plans: outlines,
  set pieces.

The page must serve both. A design that only supports an ordered list of scenes
handles the second and fails the first.

Common templates a GM outlines from — offer them, do not enforce them:
- Five-Room Dungeon: Entrance, Obstacle, Setback, Climax, Reward
- Five-Node Mystery: Hook, three points of interest, Reveal
- The Quest: Hook, Acquisition, Challenges, Complications, Closure

Show each scene's beat label so the adventure's shape is readable at a glance — a GM
should see "three complications and no payoff" without reading.

Hooks are dramatic challenges, categorised COMBAT / EXPLORATION / INVESTIGATION /
SOCIAL. Show the mix, so an adventure that is four combats and nothing else is
visible as such.

## The critical distinction to design

READ-ALOUD text and GM NOTES must be impossible to confuse. Reading a secret aloud
at the table cannot be taken back. They need genuinely different visual treatment —
not just different labels. Read-aloud is performed; GM notes are private.

## The AI relationship

The GM can ask for help at any level: "give me three hooks", "what could go wrong in
this scene", "draft an NPC for this". Design how that request and its result appear.

Two rules:
1. Everything the AI produces is a DRAFT the GM accepts, edits, or discards. Nothing
   is saved by generating it.
2. AI-generated content must be visibly marked as such until accepted, so the GM
   always knows what they wrote versus what was suggested.

Design the accept / edit / discard interaction. This is the page's most important
mechanic.

## Screens to produce

1. Adventure list — existing adventures, with status and a create affordance
2. Adventure editor — the main screen, all of the above
2b. The clue board — all clues for this adventure, which secret each points to, and
    a clear warning where an essential secret has fewer than three clues
3. Empty state — a new adventure with nothing in it yet. This is where a GM most
   needs the AI, so make the offer of help prominent rather than an afterthought.
4. An AI proposal in place — showing a generated hook or scene awaiting acceptance
5. Mobile (≤900px) — authoring on a phone is unlikely, but reading and light editing
   should work

## Design system

Reuse the existing tokens exactly:
- Backgrounds #0A0C0F app, #12141A cards, #1A1D25 raised
- Text #F8FAFC primary, #CBD5E1 secondary, #64748B muted
- Accent #E8B87A (amber-gold), success #7FD4A0
- Crimson Pro for headings and titles, Inter for UI, JetBrains Mono for eyebrow
  labels (uppercase, letter-spacing .06em, 12px)
- Radii 10-11px inputs and buttons, 14px cards
- The floating nav rail and 72px header from the workspace

Suggested: give Creative mode its own accent alongside the amber — something that
signals invention without breaking the palette. Violet reads as generative and does
not collide with the existing relationship colours (ally green, enemy red, family
amber, professional blue, neutral grey).

## Explicitly not wanted

- No Tailwind-generic look. This is a dark, image-forward, characterful tool.
- Not a form. It is a writing surface with structure, closer to a document editor
  than a settings page.
- No chat transcript as the primary interface. The AI assists the document; it is not
  the document.
````

---

## Why the prompt says what it says

**The whole brief is calibrated against the
[X&K Adventure Design Cheat Sheet](https://www.reddit.com/r/rpg/comments/14a2h61/)**, which
synthesises Justin Alexander, Sly Flourish, Matt Colville, Dungeon World, and others. Its
governing principle — *"prepare situations, not plots"* and *"prioritise flexible tools over
excessive plans"* — is why the page must support procedural structures and not only ordered
scenes.

**"Visibly different from the Research panel."** The mode separation is the safety property
in [ADR-0012](../adr/adr-0012-two-ai-modes.md). If Creative mode looks identical to Research
mode, a GM has to remember which they are in — the failure the whole design avoids.

**"Read-aloud and GM notes must be impossible to confuse."** DEC-008 in the data model.
Reading a secret aloud is unrecoverable at the table, so the distinction has to be visual
rather than a label.

**"Everything is a draft the GM accepts."** The proposal rule from
[ADR-0011](../adr/adr-0011-assistant-tools.md). No AI output reaches campaign data without
confirmation, and this page is where that interaction is most visible.

**Templates offered, not enforced.** Three common ones use three different beat
vocabularies, so a fixed set would privilege one. They are prompts for a GM outlining, not a
schema (DEC-011).

**"Clues NOT owned by a scene."** The three-clue rule: any essential secret needs at least
three routes to it, because players miss things. A clue buried in one scene's description is
the single point of failure that rule exists to prevent (DEC-009). The clue board makes the
check visible rather than leaving it to the GM to remember.

**"Fronts are a link, not an edit surface."** A front advances whether or not the PCs engage
and drives several adventures, so it belongs to the campaign (DEC-010). Editing it from
inside one adventure would imply it ends when that adventure does.

**"Not a form."** The GM is writing. A settings-page treatment of an authoring surface is
the most likely way this page comes out wrong.

**"Empty state where the AI offer is prominent."** A new adventure with nothing in it is
exactly when help is most valuable, and empty states are usually designed last if at all.

## After the design comes back

1. Publish it and add the link to [overview.md](overview.md) alongside the workspace
   prototype.
2. Transcribe any new tokens into [reference.md](reference.md) — particularly the Creative
   mode accent, if one is introduced.
3. Close gaps 6 and 7 in [mvp-scope.md](../mvp-scope.md).
4. If the design introduces states the data model cannot represent, that is a finding worth
   an ADR rather than a quiet schema change.
