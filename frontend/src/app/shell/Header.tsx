import type { Campaign } from "../../domains/campaign";
import styles from "./Header.module.css";

type HeaderProps = {
  campaign: Campaign;
};

export function Header({ campaign }: HeaderProps) {
  return (
    <header className={styles.header}>
      <div>
        <div className={styles.name}>{campaign.name}</div>
        <div className={styles.meta}>
          Session {campaign.sessionNumber} · {campaign.system}
        </div>
      </div>
      <button type="button" className={styles.avatar} aria-label="Settings">
        PM
      </button>
    </header>
  );
}
