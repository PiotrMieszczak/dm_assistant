import type { HTMLAttributes } from "react";
import styles from "./PageTitle.module.css";

/** 30px Crimson Pro page title. */
export function PageTitle({ className, ...rest }: HTMLAttributes<HTMLHeadingElement>) {
  return <h1 className={[styles.title, className].filter(Boolean).join(" ")} {...rest} />;
}

/** 20px Crimson Pro section heading. */
export function SectionTitle({ className, ...rest }: HTMLAttributes<HTMLHeadingElement>) {
  return <h2 className={[styles.section, className].filter(Boolean).join(" ")} {...rest} />;
}
