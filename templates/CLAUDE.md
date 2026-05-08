<!--
  CLAUDE.md — persistent project context, auto-loaded by Claude Code into every session.

  Source: /engineering/claude-code-best-practices (the canonical 5-section structure)
  Source: /engineering/effective-context-engineering-for-ai-agents (keep it short — context is a
          finite attention budget; every token here competes for the model's recall).

  Replace every <TODO> below. Delete sections that don't apply. Do NOT pad to "feel complete" —
  Anthropic's own posts call out exhaustive prompts as an anti-pattern.
-->

# Project: <TODO project name>

<!-- Three to five sentences max. State what the project IS and what it is NOT. -->
- Stack: <TODO e.g. TypeScript + Next.js + Postgres>
- Entry point: `<TODO src/index.ts>`
- Architecture: <TODO one line, e.g. "REST API → service layer → repo → DB">
- Out of scope: <TODO what this project does NOT do, to prevent Claude scope-creeping>

## 1. Bash commands you may run without asking

<!-- These should match the `permissions.allow` list in .claude/settings.json. -->
- `<TODO npm run build>` — compile
- `<TODO npm test>` — run unit tests
- `<TODO npm run lint>` — eslint + prettier check
- `<TODO npm run typecheck>` — type checking
- `git status`, `git diff`, `git log` — read-only git inspection

## 2. Code style

<!-- Be specific and enforceable. Vague style guides waste tokens.
     Source: /engineering/effective-context-engineering-for-ai-agents
     ("right altitude": specific enough to guide, flexible enough to leave heuristic room). -->
- <TODO e.g. Prefer named exports; one component per file.>
- <TODO e.g. No `any` in TypeScript; use `unknown` and narrow.>
- <TODO e.g. Errors thrown from `src/errors.ts`; never `throw "string"`.>
- <TODO e.g. Formatting handled by prettier — DO NOT hand-format.>

## 3. Testing rules

<!-- Source: /engineering/claude-code-best-practices (TDD is one of the explicitly recommended workflows). -->
- <TODO e.g. Every new function in `src/` needs a test in `__tests__/`.>
- <TODO e.g. Use Vitest. Mock external HTTP with `msw`.>
- After any edit, run `<TODO npm test>` before declaring the task done.

## 4. Repository etiquette

<!-- Source: /engineering/claude-code-best-practices (commit early/often; clean git state for autonomous work). -->
- Branch naming: `feat/<ticket>-<slug>`, `fix/<ticket>-<slug>`.
- Commit messages: imperative, ≤72 chars subject; body explains *why*.
- NEVER commit to `main` directly. Open a PR.
- Run `<TODO npm run lint && npm test>` before every commit.

## 5. Files Claude should read first when exploring

<!-- "Just-in-time" context: lightweight pointers Claude expands on demand instead of loading everything upfront.
     Source: /engineering/effective-context-engineering-for-ai-agents -->
- `<TODO src/index.ts>` — entry
- `<TODO src/types.ts>` — domain types
- `<TODO docs/architecture.md>` — system diagram + invariants
- `<TODO db/schema.sql>` — canonical schema

## 6. Things Claude should NOT do

<!-- Anti-patterns specific to this repo. Source: /engineering/claude-code-best-practices -->
- Do NOT edit files under `<TODO vendor/>` or `<TODO node_modules/>`.
- Do NOT run `<TODO npm install>` without asking — lockfile is curated.
- Do NOT modify `<TODO db/migrations/*>` after they have been applied.
- Do NOT delete tests to make a build pass.
- Do NOT introduce new dependencies without flagging them in the plan.

## 7. When stuck or uncertain

<!-- Source: /engineering/claude-code-best-practices ("course-correct early and often")
     Source: /engineering/multi-agent-research-system ("start wide, then narrow down") -->
- If exploring an unfamiliar area: start broad (`grep`, `glob`), then drill in.
- If a tool returns an error: read the error fully; do NOT retry blindly.
- If the plan exceeds ~5 steps: write it to `PLAN.md` first, get my approval before coding.
- If context is filling up: invoke `/compact-resume` and continue in a fresh session.
- If a requirement is ambiguous: ask. A clarifying question is cheaper than rework.
