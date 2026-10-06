import styles from "./QuickPrompts.module.css";

type QuickPromptsProps = {
  prompts: string[];
};

export function QuickPrompts({ prompts }: QuickPromptsProps) {
  return (
    <div className={styles.prompts}>
      {prompts.map((prompt) => (
        <button key={prompt} type="button" className={styles.chip}>
          {prompt}
        </button>
      ))}
    </div>
  );
}
