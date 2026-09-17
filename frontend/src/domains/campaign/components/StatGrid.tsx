import { StatTile } from "../../../ui/components";
import type { CampaignStats } from "../model/types";
import styles from "./StatGrid.module.css";

type StatGridProps = {
  stats: CampaignStats;
};

/** The Overview's 4-up stat grid. Two columns at =<900px. */
export function StatGrid({ stats }: StatGridProps) {
  return (
    <div className={styles.grid}>
      <StatTile label="NPCs" value={stats.npcs} />
      <StatTile label="Factions" value={stats.factions} />
      <StatTile label="Active quests" value={stats.activeQuests} />
      <StatTile label="Documents" value={stats.documents} />
    </div>
  );
}
