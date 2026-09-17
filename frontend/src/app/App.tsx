import { CAMPAIGN } from "../domains/campaign";
import { Overview } from "../screens/workspace/Overview";
import { WorkspaceShell } from "./shell/WorkspaceShell";

export function App() {
  return (
    <WorkspaceShell campaign={CAMPAIGN} activeView="overview">
      <Overview />
    </WorkspaceShell>
  );
}
