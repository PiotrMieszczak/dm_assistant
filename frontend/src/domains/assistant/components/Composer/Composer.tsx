import { useRef } from "react";
import styles from "./Composer.module.css";

const MAX_HEIGHT = 120;

export function Composer() {
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const grow = () => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, MAX_HEIGHT)}px`;
  };

  return (
    <form className={styles.composer} onSubmit={(event) => event.preventDefault()}>
      <button type="button" className={styles.icon} aria-label="Attach">
        +
      </button>
      <textarea
        ref={inputRef}
        className={styles.input}
        rows={1}
        placeholder="Ask, search, or draft a scene…"
        onInput={grow}
      />
      <button type="submit" className={styles.send} aria-label="Send">
        ➤
      </button>
    </form>
  );
}
