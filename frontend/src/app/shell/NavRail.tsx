import { NAV_ITEMS } from "./navItems";
import styles from "./NavRail.module.css";

type NavRailProps = {
  active: string;
};

export function NavRail({ active }: NavRailProps) {
  return (
    <nav className={styles.rail} aria-label="Workspace">
      {NAV_ITEMS.map((item) => {
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
