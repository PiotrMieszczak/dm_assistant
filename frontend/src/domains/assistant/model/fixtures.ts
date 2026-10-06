import type { Conversation } from "./types";

/** Placeholder transcript until the assistant API exists. Short enough that
 *  quick-prompt chips still show. No citations — that presentation is a
 *  design gap. */

export const CONVERSATION: Conversation = {
  id: "conv-research-1",
  mode: "research",
  provider: "Claude",
  messages: [
    {
      id: "m1",
      role: "user",
      content: "What did we establish about Doran Vey?",
      createdAt: "2026-10-03T18:12:00Z",
    },
    {
      id: "m2",
      role: "assistant",
      content:
        "Doran Vey is a Pale Court contact. After Session 14 the party's " +
        "disposition toward him moved from neutral to ally — they bargained " +
        "instead of fighting.",
      createdAt: "2026-10-03T18:12:08Z",
      toolLabel: "Searched indexed material",
    },
  ],
};

export const QUICK_PROMPTS = [
  "Opportunity attacks",
  "Summarise last session",
  "Who is Doran Vey?",
];
