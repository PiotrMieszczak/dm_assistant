---
name: task-flow
description: The four-stage flow for starting any piece of work in this repository - research, then an issue with acceptance criteria, then the project board, then a branch and PR wired to that issue. Use when starting a new task, opening an issue, asking "what should I work on", picking work off the board, or when a request arrives as a bare feature idea with no issue behind it.
model-hint: sonnet
---

# Task flow

Four stages. Each produces an artefact the next one consumes, so work never starts from a
sentence in a chat window.

```
Research  →  Issue  →  Board  →  Branch + PR
 options      goal,     Research    CI + PR Agent
 and risks    scope,    → Ready →   run against
              criteria  In progress the diff
                        → Review
                        → Done
```

**The rule that makes it worth the ceremony:** an issue without acceptance criteria is a
wish, not a task. If you cannot write down what "done" looks like, the research stage is
not finished.

## 1. Research

Find out what actually has to change before proposing how.

- Read the `docs/` pages the task touches — one or two, per [CLAUDE.md](../../../CLAUDE.md)
- Grep the code the change would land in. Name real files, not guesses
- Check whether an ADR already decides this. If the task contradicts one, that is the
  finding — say so before writing the issue
- List the options with their trade-offs, and the risks of each

Output is not a commit. It is the material the issue is written from.

## 2. Issue

Five sections. Skip none — an empty section is itself information.

```markdown
## Goal
One sentence. What changes for the user or the system.

## Context
Why now. Link the docs pages and ADRs the research turned up.

## Scope
In scope: ...
Out of scope: ...

## Acceptance criteria
- [ ] Observable, checkable statements
- [ ] Written so someone else could verify them without asking you

## Open questions
Anything unresolved. "None" is a valid answer.
```

Create it:

```bash
gh issue create --title "..." --body-file issue.md --label enhancement
```

**Acceptance criteria are the deliverable of this stage.** Cite `AC-0nn` ids from
[docs/mvp-scope.md](../../../docs/mvp-scope.md) where one already covers the work, rather
than inventing a parallel vocabulary.

## 3. Board

The issue goes on the project board, in `Research` if it needs more work, `Ready` if the
criteria are agreed.

Columns: **Research → Ready → In progress → Review → Done**

```bash
gh project item-add <number> --owner PiotrMieszczak --url <issue-url>
```

> **`gh project` needs gh 2.31 or newer.** This machine runs 2.23, where the subcommand
> does not exist. Either upgrade, or add the item from the board UI — the flow does not
> depend on the CLI path.

Move the card when the work moves. A board that lags the branch is worse than no board.

## 4. Branch and PR

Branch names carry the type and the issue:

```
feat/<issue>-<slug>      fix/<issue>-<slug>      chore/<issue>-<slug>
ci/<slug>                docs/<slug>
```

```bash
git checkout -b feat/12-adventure-clue-board
```

Open the PR against `main`, linked so the issue closes on merge:

```bash
gh pr create --fill --base main --body "Closes #12"
```

`Closes #12` is what ties the two together — without it the issue stays open after merge
and the board never reaches Done.

On the PR, automatically:

- **CI** — lint, test, build (`.github/workflows/ci.yml`)
- **PR Agent** — review on `/review`, description on `/describe`
  (`.github/workflows/pr-agent.yml`)

Use the template in [.github/pull_request_template.md](../../../.github/pull_request_template.md):
description, how to test, notes, and a four-item definition of done.

## Where this bends

**A one-line fix does not need four stages.** A typo, a dead link, a version bump — commit
it. The flow exists for work whose scope is arguable, and a fix with no arguable scope is
not that.

**Research can end the task.** "This is already handled by X" is a complete outcome. Close
it with that as the reason rather than manufacturing an issue to justify the time.

**An issue may be split.** If the acceptance criteria need more than about five checkboxes,
it is probably two issues. Splitting at issue time is cheap; splitting mid-branch is not.
