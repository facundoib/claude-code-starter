---
name: compact-resume
description: Use when context is filling up but the task is not done. Writes a structured progress file, then clears the session. The next session reads the progress file and continues seamlessly.
---

# /compact-resume — long-horizon session bridge

You are about to **write progress and clear the context**. The next session will read the progress file as its starting state.

## Procedure

1. **Write `claude-progress.txt`** in the repo root, overwriting if it exists. Use exactly this structure:

```
# Claude session progress
# Updated: <ISO 8601 timestamp>
# Repo: <repo name + branch>

## Goal
<one paragraph: what is this multi-session task working toward?>

## Completed
- <task 1, with file paths or commits referenced>
- <task 2>
- ...

## In progress
- <current step + state, e.g. "Implementing handler for X — tests written but failing on edge case Y">

## Open decisions
- <any architectural or design choice the next session needs to either honor or revisit>

## Open bugs / blockers
- <anything broken that's not yet fixed>

## Next 1-3 actions
1. <very specific next step>
2. ...
3. ...

## Files of interest
<list of files the next session should read first to reload context>

## Anti-patterns to remember
<things you tried that didn't work, so the next session doesn't repeat them>
```

2. **Tell the user** the progress file is written, list the next 1-3 actions for confirmation.
3. **Run `/clear`** when the user confirms.

## How the next session continues

The next Claude session should be invoked with: "Read `claude-progress.txt` and continue from the Next actions section." That's it — the progress file replaces session memory.

## When to use this vs `/compact`

- `/compact` (built-in) — summarizes the conversation and continues in the same session. Good for staying in flow when context is moderately full.
- `/compact-resume` (this skill) — full handoff to a fresh session. Use when context is near full, when you want a clean slate, or when the task spans hours/days.

## Why

Source: `/engineering/effective-harnesses-for-long-running-agents` — the documented two-agent harness (initializer + coder) uses `claude-progress.txt` as the canonical handoff artifact. Same pattern; this skill exposes it as a slash command.

Source: `/engineering/effective-context-engineering-for-ai-agents` — structured note-taking is the documented antidote to context rot for long horizons; the `claude-progress.txt` format above is structured note-taking.

Source: `/engineering/building-c-compiler` — the C compiler build used ~2,000 Claude sessions chained via progress files; the pattern scales.
