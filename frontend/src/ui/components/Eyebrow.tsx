import type { HTMLAttributes } from "react";
import styles from "./Eyebrow.module.css";

/** Uppercase mono label. Sits above a value or section. */
export function Eyebrow({ className, ...rest }: HTMLAttributes<HTMLElement>) {
  return <p className={[styles.eyebrow, className].filter(Boolean).join(" ")} {...rest} />;
}
