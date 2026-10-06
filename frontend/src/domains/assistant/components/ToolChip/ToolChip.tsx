import styles from "./ToolChip.module.css";

type ToolChipProps = {
  label: string;
};

export function ToolChip({ label }: ToolChipProps) {
  return (
    <div className={styles.tool}>
      <span aria-hidden>✓</span>
      {label}
    </div>
  );
}
