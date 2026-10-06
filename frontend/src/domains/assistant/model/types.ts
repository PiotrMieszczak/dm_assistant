/** Shapes the Research panel renders. Mirrors docs/data-model.md Conversation
 *  and Message, plus the mode the interface must name (AC-016, ADR-0012). */

export type Mode = "research";

export type MessageRole = "user" | "assistant";

export type Message = {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: string;
  toolLabel?: string;
};

export type Conversation = {
  id: string;
  mode: Mode;
  provider: string;
  messages: Message[];
};
