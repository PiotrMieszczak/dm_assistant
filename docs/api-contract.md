# API Contract

Base path `/api/v1`. JSON throughout, except the assistant stream (SSE) and uploads
(multipart). All resources except campaigns are scoped to a campaign and enforce that
scope server-side (BND-003).

## Conventions

- IDs are integers except `campaign.id`, which is a slug
- Timestamps are ISO 8601 UTC
- Errors: `{ "detail": "message" }` with a conventional status code
- Collections return bare arrays; v1 has no pagination (single-user scale)

## Campaigns

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/campaigns` | List for the picker |
| `POST` | `/campaigns` | Create — `name` and `system` required |
| `GET` | `/campaigns/{id}` | Single campaign |
| `PATCH` | `/campaigns/{id}` | Rename, change image or tint |
| `DELETE` | `/campaigns/{id}` | Delete campaign and all contents |

```jsonc
// POST /campaigns
{ "name": "Ashfall Reach", "system": "D&D 2024", "tint": "#E8B87A" }
// 201
{ "id": "ashfall", "name": "Ashfall Reach", "system": "D&D 2024",
  "tint": "#E8B87A", "imageUrl": null, "sessionCount": 0, "lastPlayedAt": null }
```

`POST /campaigns/{id}/image` — multipart, sets the banner.

## Documents

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/campaigns/{cid}/documents` | List with status and progress |
| `POST` | `/campaigns/{cid}/documents` | Upload (multipart) — returns `202` |
| `GET` | `/campaigns/{cid}/documents/{id}` | Single document, for polling |
| `POST` | `/campaigns/{cid}/documents/{id}/retry` | Re-run a failed extraction |
| `DELETE` | `/campaigns/{cid}/documents/{id}` | Remove document, chunks, and index rows |

```jsonc
// GET /campaigns/ashfall/documents
[
  { "id": 1, "filename": "Core Rulebook v3.pdf", "kind": "PDF", "pageCount": 412,
    "meta": "stat blocks · rules", "status": "indexed", "progress": 100, "error": null },
  { "id": 3, "filename": "Bestiary — Regional.pdf", "kind": "PDF", "pageCount": 156,
    "meta": "extracting stat blocks", "status": "processing", "progress": 64, "error": null }
]
```

Upload returns `202 Accepted` immediately with `status: "queued"`. The client polls this
list while any document is `queued` or `processing`, then stops (PRIN-003 — upload never
blocks).

## Search

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/campaigns/{cid}/search?q=` | FTS5 search over indexed chunks |

```jsonc
[{ "chunkId": 812, "documentId": 1, "filename": "Core Rulebook v3.pdf",
   "heading": "Opportunity Attacks", "pageFrom": 195, "pageTo": 195,
   "snippet": "…when a hostile creature <mark>leaves your reach</mark>…", "score": 4.21 }]
```

## Characters

Covers NPCs and player characters; `isPlayer` selects the list.

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/campaigns/{cid}/characters?isPlayer=&relationship=` | Filtered list |
| `POST` | `/campaigns/{cid}/characters` | Create |
| `GET` | `/campaigns/{cid}/characters/{id}` | Detail with connections |
| `PATCH` | `/campaigns/{cid}/characters/{id}` | Update |
| `DELETE` | `/campaigns/{cid}/characters/{id}` | Delete |
| `POST` | `/campaigns/{cid}/characters/{id}/portrait` | Multipart upload |

```jsonc
{ "id": 4, "name": "Brother Cael", "role": "Human Cleric", "level": 5,
  "isPlayer": true, "relationship": "ally", "location": "The Party",
  "disposition": "Steadfast", "lastSeen": "Session 13",
  "armorClass": "18", "hitPoints": "47", "speed": "30 ft",
  "stats": [{ "k": "STR", "v": 14 }, { "k": "WIS", "v": 17 }],
  "tags": ["Healer", "Faith"],
  "quote": "The Light does not ask who deserves it.",
  "notes": "Ties the party to Mother Ansel's temple faction.",
  "portraitUrl": null,
  "playerProfile": { "playerName": "Jordan Kim", "class": "Cleric (Light)",
                     "race": "Human", "background": "Acolyte", "xp": "6,500",
                     "pronouns": "they/them", "bonds": "Sworn to the temple…" },
  "connections": [{ "targetType": "character", "targetId": 7,
                    "name": "Mother Ansel", "kind": "ally" }] }
```

`notes` is GM-private and excluded from assistant context by default (DEC-004).

## Factions

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/campaigns/{cid}/factions` | List |
| `POST` | `/campaigns/{cid}/factions` | Create |
| `GET` | `/campaigns/{cid}/factions/{id}` | Detail with members and connections |
| `PATCH` | `/campaigns/{cid}/factions/{id}` | Update |
| `DELETE` | `/campaigns/{cid}/factions/{id}` | Delete |
| `PUT` | `/campaigns/{cid}/factions/{id}/members` | Replace membership (character ids) |

## Relationships

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/campaigns/{cid}/relationships` | All edges, for the graph |
| `POST` | `/campaigns/{cid}/relationships` | Create an edge |
| `PATCH` | `/campaigns/{cid}/relationships/{id}` | Change kind |
| `DELETE` | `/campaigns/{cid}/relationships/{id}` | Remove |

```jsonc
// GET /campaigns/ashfall/graph — nodes and edges ready to render
{ "nodes": [{ "id": "character:4", "type": "character", "name": "Brother Cael",
              "role": "Human Cleric", "level": 5, "faction": "The Ashfall Temple",
              "relationship": "ally" }],
  "edges": [{ "id": 12, "source": "character:4", "target": "faction:2", "kind": "ally" }] }
```

## Quests

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/campaigns/{cid}/quests?status=` | List, optionally by status tab |
| `POST` | `/campaigns/{cid}/quests` | Create, optionally with `parentQuestId` |
| `PATCH` | `/campaigns/{cid}/quests/{id}` | Update fields, progress, or status |
| `DELETE` | `/campaigns/{cid}/quests/{id}` | Delete |

Status transitions — including Reactivate from `failed` or `inactive` back to
`inprogress` — are ordinary `PATCH` calls on `status`.

## Sessions

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/campaigns/{cid}/sessions` | List, newest first |
| `POST` | `/campaigns/{cid}/sessions` | Create from the composer |
| `PATCH` | `/campaigns/{cid}/sessions/{id}` | Update |
| `DELETE` | `/campaigns/{cid}/sessions/{id}` | Delete |

Creating or updating a session re-chunks and re-indexes its body so past sessions are
retrievable alongside documents.

## Assistant

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/campaigns/{cid}/conversations` | List |
| `POST` | `/campaigns/{cid}/conversations` | Start one |
| `GET` | `/campaigns/{cid}/conversations/{id}/messages` | History with citations |
| `POST` | `/campaigns/{cid}/conversations/{id}/messages` | Send; responds as SSE |

**Streaming response.** `text/event-stream`:

```
event: tool
data: {"label":"Searched 3 documents"}

event: token
data: {"text":"Opportunity attacks trigger when"}

event: citation
data: {"chunkId":812,"documentId":1,"filename":"Core Rulebook v3.pdf","pageFrom":195}

event: done
data: {"messageId":57}
```

`tool` events drive the green check chips. `citation` events populate source references
(AC-002). When retrieval finds nothing relevant, the assistant says so explicitly rather
than answering unsourced (AC-003).

## Settings

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/settings` | Profile and provider |
| `PATCH` | `/settings` | Update profile fields or `provider` |
| `POST` | `/settings/avatar` | Multipart upload |
| `GET` | `/settings/providers` | Available providers and reachability |

```jsonc
// GET /settings/providers
[{ "id": "claude", "label": "Claude", "available": true },
 { "id": "ollama", "label": "Ollama", "available": false,
   "detail": "No response at http://localhost:11434" }]
```

Switching providers takes effect on the next message with no restart (AC-004).
