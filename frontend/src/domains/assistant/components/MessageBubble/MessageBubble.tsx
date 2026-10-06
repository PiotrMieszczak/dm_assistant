import type { Message } from "../../model/types";
import { ToolChip } from "../ToolChip";
import styles from "./MessageBubble.module.css";

type MessageBubbleProps = {
  message: Message;
};

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  return (
    <article
      className={[styles.row, isUser ? styles.userRow : styles.assistantRow].join(" ")}
    >
      <div className={[styles.bubble, isUser ? styles.user : styles.assistant].join(" ")}>
        {message.toolLabel && <ToolChip label={message.toolLabel} />}
        <p className={styles.body}>{message.content}</p>
      </div>
    </article>
  );
}
