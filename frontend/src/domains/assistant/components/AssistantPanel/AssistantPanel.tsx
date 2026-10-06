import { CONVERSATION, QUICK_PROMPTS } from "../../model/fixtures";
import { Composer } from "../Composer";
import { MessageList } from "../MessageList";
import { QuickPrompts } from "../QuickPrompts";
import styles from "./AssistantPanel.module.css";

type AssistantPanelProps = {
  onClose: () => void;
};

const SHORT_THREAD = 4;

export function AssistantPanel({ onClose }: AssistantPanelProps) {
  const { mode, provider, messages } = CONVERSATION;
  const showPrompts = messages.length <= SHORT_THREAD;

  return (
    <section className={styles.panel} aria-label="Assistant">
      <header className={styles.header}>
        <div className={styles.spark} aria-hidden>
          ✦
        </div>
        <div className={styles.titles}>
          <div className={styles.title}>Assistant</div>
          <div className={styles.subtitle}>
            <span className={styles.mode}>{modeLabel(mode)}</span>
            Grounded in indexed material
          </div>
        </div>
        <span className={styles.provider}>
          <span className={styles.dot} aria-hidden />
          {provider}
        </span>
        <button type="button" className={styles.close} aria-label="Close assistant" onClick={onClose}>
          ×
        </button>
      </header>

      <MessageList messages={messages} />
      {showPrompts && <QuickPrompts prompts={QUICK_PROMPTS} />}
      <Composer />
    </section>
  );
}

function modeLabel(mode: typeof CONVERSATION.mode) {
  return mode === "research" ? "Research" : mode;
}
