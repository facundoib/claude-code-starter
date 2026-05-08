---
name: eval
description: Use BEFORE any prompt change, tool change, model swap, or skill edit. Runs the eval harness, diffs against the last committed results, flags regressions.
---

# /eval — run the lightweight eval harness

You are running the project's eval suite as a regression check. Do NOT modify the eval tasks themselves in this run — that's a separate workflow.

## Procedure

1. **Confirm the harness exists**:
   - `evals/tasks.jsonl` (the test set)
   - `evals/run.py` (the runner)
   - `evals/judge.py` (the LLM-as-judge)
   - `evals/last_results.json` (committed baseline)

   If any are missing, tell the user and stop. Do not synthesize fake results.

2. **Run the harness**:
   ```bash
   python evals/run.py
   ```

   Capture stdout. Note: each task is run **3 times** to control for non-determinism. The runner writes `evals/results/<timestamp>.json`.

3. **Diff against the baseline** (`evals/last_results.json`):
   - Pass-rate delta (current vs baseline).
   - Per-task regressions: tasks that passed in baseline but fail now.
   - Per-task improvements: tasks that fail in baseline but pass now.
   - Variance change: tasks where the std deviation across the 3 runs grew significantly.

4. **Print a report** with these sections:
   - Headline: `Pass rate: X% (Δ +/- Y pp vs baseline)`
   - Regressions: list, with task IDs and the failure mode.
   - Improvements: list, with task IDs.
   - Token cost: total in + out, vs baseline.
   - Wall time: total, vs baseline.

5. **Decision**:
   - If no regressions and pass rate >= baseline: print "Safe to commit changes. Run `cp evals/results/<timestamp>.json evals/last_results.json` to update baseline."
   - If regressions: print "REGRESSION DETECTED. Do NOT update baseline. Investigate failures before committing."

## When to invoke

- Before committing changes to `CLAUDE.md`.
- Before committing changes to `.claude/skills/*`.
- Before changing the model (`claude-sonnet-4-6` ↔ `claude-opus-4-7` etc).
- Before adding or removing tools / MCP servers.
- After any prompt-engineering tweak that touches behavior.

## When NOT to invoke

- Cosmetic doc changes (typos, formatting).
- Changes to evals themselves (run them, but don't compare to a baseline that no longer applies).

## Why

Source: `/engineering/demystifying-evals-for-ai-agents` — start with 20-50 tasks from real failures, run them every release. Don't wait until you have hundreds.

Source: `/engineering/multi-agent-research-system` — a single-rubric LLM judge with one 0.0-1.0 score per task is the pattern that matched human raters best. Multiple rubrics in one call introduce noise.

Source: `/engineering/infrastructure-noise` — agents are non-deterministic between runs; report mean and variance, not point estimates. That's why this harness runs each task 3 times.

Source: `/engineering/april-23-postmortem` — Anthropic's own incident: a verbosity instruction degraded Opus 4.6 and 4.7 evals by 3pp. Without continuous evals, behavior regressions are invisible until users complain.
