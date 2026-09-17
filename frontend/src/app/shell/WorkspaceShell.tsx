import type { ReactNode } from "react";
import type { Campaign } from "../../domains/campaign";
import { Header } from "./Header";
import { NavRail } from "./NavRail";
import { TabBar } from "./TabBar";
import styles from "./WorkspaceShell.module.css";

type WorkspaceShellProps = {
  campaign: Campaign;
  activeView: string;
  children: ReactNode;
};

export function WorkspaceShell({ campaign, activeView, children }: WorkspaceShellProps) {
  return (
    <div className={styles.shell}>
      <Header campaign={campaign} />
      <NavRail active={activeView} />
      <main className={styles.main}>{children}</main>
      <TabBar active={activeView} />
      <button type="button" className={styles.fab}>
        <span aria-hidden>✦</span>
        <span className={styles.fabLabel}>Assistant</span>
      </button>
    </div>
  );
}
