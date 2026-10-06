import type { HTMLAttributes } from "react";
import styles from "./Card.module.css";

type CardProps = HTMLAttributes<HTMLDivElement> & {
  /** Lifts the border on hover. For cards that respond to pointer input. */
  interactive?: boolean;
};

export function Card({ interactive, className, ...rest }: CardProps) {
  const classes = [styles.card, interactive && styles.interactive, className]
    .filter(Boolean)
    .join(" ");
  return <div className={classes} {...rest} />;
}
