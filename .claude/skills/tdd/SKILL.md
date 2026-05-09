---
name: tdd
description: Use when implementing a new feature or fix that has clear acceptance criteria. Writes tests first, confirms they fail for the right reason, then implements until green. Commits on green.
---

# /tdd — test-first loop

You are operating in **TDD mode**. Code does NOT come before tests.

## Procedure

1. **Restate the requirement** in one paragraph. If anything is ambiguous, ask before continuing.
2. **Identify or create the test file** matching the project's convention (e.g. `__tests__/<name>.test.ts`, `tests/test_<name>.py`).
3. **Write the failing tests**:
   - Cover the golden path.
   - Cover at least 2 edge cases the requirement implies.
   - Cover 1 error case if applicable.
4. **Run the tests** with the project's test command. Verify they fail. Read the failure output and confirm they fail **for the reason you expect** (not because of a typo or import error). If they pass on the first run, the test is wrong — fix it.
5. **Implement** the minimum code to make the tests pass. Do NOT add untested behavior.
6. **Run the tests again**. Iterate until green.
7. **Run the full suite** (not just your new tests) to confirm no regressions.
8. **Commit** with an imperative subject line (≤72 chars) referencing the requirement. Body explains *why*, not what.
9. **Stop**. Print "TDD cycle complete. N tests added. All green."

## Anti-patterns to refuse

- Deleting or weakening tests to make a build pass.
- Mocking the unit-under-test.
- Writing tests *after* the implementation (call it what it is — that's not TDD).
- Asserting against implementation details (private methods, internal state) instead of behavior.

## Position in the loop

Comes after `/plan` (the plan defines what "done" looks like; tests encode it). Comes before `/review`, which evaluates the resulting diff with fresh context. If the change touches `CLAUDE.md`, `.claude/skills/*`, or anything that affects model behavior, also run `/eval` after to catch regressions (`/engineering/april-23-postmortem`).

## Why

Source: `/engineering/claude-code-best-practices` — TDD is one of the explicitly recommended workflows; tests-first creates a verifiable contract for "done".

Source: `/engineering/building-c-compiler` — "extremely high-quality tests" were the load-bearing component that let 16 parallel Claude instances ship 100K LOC of compiler code. Test quality is the leverage point.

Source: `/engineering/demystifying-evals-for-ai-agents` — graders that check end-state (did it work?) beat graders that check the path. Same principle applies to your tests.
