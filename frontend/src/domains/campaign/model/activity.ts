import type { ActivityKind } from "./types";

/** Relationship and status tokens, keyed by what produced the entry.
 *  Pure derivation — no component decides its own colour. */
const TONE_BY_KIND: Record<ActivityKind, string> = {
  session: "var(--accent)",
  npc: "var(--rel-professional)",
  quest: "var(--quest-subquest)",
  document: "var(--success)",
};

const LABEL_BY_KIND: Record<ActivityKind, string> = {
  session: "Session",
  npc: "NPC",
  quest: "Quest",
  document: "Document",
};

export function toneFor(kind: ActivityKind): string {
  return TONE_BY_KIND[kind];
}

export function labelFor(kind: ActivityKind): string {
  return LABEL_BY_KIND[kind];
}
