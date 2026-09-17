import { Card } from "./Card";
import { Eyebrow } from "./Eyebrow";
import styles from "./StatTile.module.css";

type StatTileProps = {
  label: string;
  value: string | number;
};

/** One cell of a stat grid: mono label over a display-font value. */
export function StatTile({ label, value }: StatTileProps) {
  return (
    <Card className={styles.tile}>
      <Eyebrow>{label}</Eyebrow>
      <span className={styles.value}>{value}</span>
    </Card>
  );
}
