/** Workspace destinations, in the order docs/design/overview.md specifies.
 *  The rail shows all eight; the mobile tab bar shows four and hides the
 *  rest behind More, so both surfaces read one list. */
export type NavItem = {
  id: string;
  label: string;
  glyph: string;
  /** Shorter label for the tab bar, where space is tight. */
  short?: string;
};

export const NAV_ITEMS: NavItem[] = [
  { id: "overview", label: "Overview", glyph: "◇", short: "Home" },
  { id: "npcs", label: "NPCs", glyph: "☾" },
  { id: "players", label: "Players", glyph: "✦", short: "Party" },
  { id: "factions", label: "Factions", glyph: "⌘" },
  { id: "quests", label: "Quest Log", glyph: "✧", short: "Quests" },
  { id: "documents", label: "Documents", glyph: "▤" },
  { id: "graph", label: "Knowledge Graph", glyph: "⊛" },
  { id: "sessions", label: "Sessions", glyph: "❍" },
];

/** The four that get their own tab; everything else lives in the More sheet. */
export const TAB_IDS = ["overview", "npcs", "players", "quests"];
