---
name: plan
description: Use BEFORE writing code on any non-trivial task. Reads the relevant files first, then produces a numbered plan in PLAN.md. Triggers extended thinking. Stops before implementing.
---

# /plan — plan-before-code gate

You are operating in **plan mode**. Do NOT write any production code in this turn.

## Procedure

1. **Read the files** the user listed (or that you identified via `grep`/`glob`). Read them fully — do not skim.
2. **Think hard** about the task. If the request says "ultrathink" or "think hard", spend an extended thinking budget proportional to the complexity.
3. **Write the plan** to `PLAN.md` (overwrite if it exists). The plan must contain:
   - **Goal**: one sentence.
   - **Files to touch**: bullet list with one-line per file describing the change.
   - **New files**: list with purpose.
   - **Tests to add**: which test files, what they cover.
   - **Risks**: anything that could break, anything ambiguous, anything you'd flag for human decision.
   - **Steps**: numbered, sequential, each step small enough to be verifiable.
   - **Out of scope**: what you are explicitly NOT doing in this task.
4. **Stop**. Print "PLAN.md written. Approve before implementing." and wait for the user.

## When to skip /plan

- Trivial single-line edits.
- Pure questions that don't change code.
- Tasks the user already pre-planned (they sent a numbered list).

## Why

Source: `/engineering/claude-code-best-practices` — the explore → plan → code → commit loop is the canonical recipe; jumping straight to code is the documented anti-pattern.

Source: `/engineering/effective-context-engineering-for-ai-agents` — extended thinking acts as a controllable scratchpad; using it before tool calls reduces wasted tokens later.

Source: `/engineering/harness-design-long-running-apps` — sprint contracts (negotiating "done" before implementing) prevent the rework cycle that dominates long-running tasks.
