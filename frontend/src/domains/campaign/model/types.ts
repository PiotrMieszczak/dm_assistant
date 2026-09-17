/** Shapes the Overview renders. Mirrors docs/data-model.md, narrowed to what
 *  this view needs — the API contract fills these in later. */

export type Campaign = {
  id: string;
  name: string;
  system: string;
  sessionNumber: number;
};

export type CampaignStats = {
  npcs: number;
  factions: number;
  activeQuests: number;
  documents: number;
};

export type ActivityKind = "session" | "npc" | "quest" | "document";

export type ActivityEntry = {
  id: string;
  kind: ActivityKind;
  title: string;
  detail: string;
  at: string;
};
