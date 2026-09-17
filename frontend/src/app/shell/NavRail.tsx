import styles from "./NavRail.module.css";

/** Rail items in the order docs/design/overview.md specifies.
 *  Navigation is inert until routing lands — this view is Overview only. */
const ITEMS = [
  { id: "overview", label: "Overview", glyph: "◇" },
  { id: "npcs", label: "NPCs", glyph: "☾" },
  { id: "players", label: "Players", glyph: "✦" },
  { id: "factions", label: "Factions", glyph: "⌘" },
  { id: "quests", label: "Quest Log", glyph: "✧" },
  { id: "documents", label: "Documents", glyph: "▤" },
  { id: "graph", label: "Knowledge Graph", glyph: "⊛" },
  { id: "sessions", label: "Sessions", glyph: "❍" },
] as const;

type NavRailProps = {
  active: string;
};

export function NavRail({ active }: NavRailProps) {
  return (
    <nav className={styles.rail} aria-label="Workspace">
      {ITEMS.map((item) => {
        const isActive = item.id === active;
        return (
          <button
            key={item.id}
            type="button"
            className={[styles.item, isActive && styles.active].filter(Boolean).join(" ")}
            aria-current={isActive ? "page" : undefined}
          >
            <span className={styles.glyph} aria-hidden>
              {item.glyph}
            </span>
            <span className={styles.label}>{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
