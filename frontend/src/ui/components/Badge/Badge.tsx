import type { HTMLAttributes } from "react";
import styles from "./Badge.module.css";

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  /** Any color token. Renders a leading dot; omit for a plain chip. */
  tone?: string;
};

export function Badge({ tone, children, className, ...rest }: BadgeProps) {
  return (
    <span className={[styles.badge, className].filter(Boolean).join(" ")} {...rest}>
      {tone && <span className={styles.dot} style={{ color: tone }} aria-hidden />}
      {children}
    </span>
  );
}
