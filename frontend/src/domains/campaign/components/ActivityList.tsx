import { Badge, Card } from "../../../ui/components";
import { labelFor, toneFor } from "../model/activity";
import type { ActivityEntry } from "../model/types";
import styles from "./ActivityList.module.css";

type ActivityListProps = {
  entries: ActivityEntry[];
};

export function ActivityList({ entries }: ActivityListProps) {
  return (
    <Card>
      <ul className={styles.list}>
        {entries.map((entry) => (
          <li key={entry.id} className={styles.row}>
            <Badge tone={toneFor(entry.kind)}>{labelFor(entry.kind)}</Badge>
            <div className={styles.body}>
              <div className={styles.title}>{entry.title}</div>
              <div className={styles.detail}>{entry.detail}</div>
            </div>
            <time className={styles.at}>{entry.at}</time>
          </li>
        ))}
      </ul>
    </Card>
  );
}
