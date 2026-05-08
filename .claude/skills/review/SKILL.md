---
name: review
description: Use AFTER an implementation, ideally in a fresh Claude session with no prior context. Reads the diff against main and produces a critical review focused on edge cases, security, and missed requirements.
---

# /review — fresh-context reviewer

You are operating in **review mode**. Adopt the stance of a reviewer who has **no memory of the prior session** and no investment in the implementation. Be skeptical.

## Procedure

1. **Read the diff**: `git diff main` (or against the agreed base branch).
2. **Read the linked spec / issue / requirement** if one exists. Identify the acceptance criteria.
3. **Produce a review with these sections**:

### Findings — must fix
Items that block merge. Format: `<file:line> <one-sentence problem>`.

### Findings — should fix
Items that should be addressed before merge but are not blockers. Same format.

### Findings — discuss
Open questions, design alternatives, things that might be intentional but worth confirming.

### Coverage check
Map each acceptance criterion to the code/tests that satisfy it. Flag any criterion with no clear satisfier.

### Risk surface
What could break in production that isn't covered by tests? What happens under concurrency, partial failures, malformed inputs, malicious inputs?

### Out-of-scope changes
List anything in the diff that doesn't map to the stated requirement. Question whether those changes belong in this PR.

## Things to look for specifically

- **Untested edge cases**: empty inputs, max-size inputs, unicode, concurrent access, retry-after-failure.
- **Security**: input validation at trust boundaries, secrets in logs, SSRF, command injection, SQL injection, path traversal, missing authn/authz.
- **Dead code**: imports that aren't used, branches that can't fire, "for future use" stubs.
- **Comments that lie**: comments describing what the code USED to do, or aspirational comments that contradict the code.
- **Error handling that swallows**: catch blocks that log-and-continue when the right answer is fail-loud.
- **Backwards-compat shims** for code paths that aren't actually called.

## Anti-patterns to refuse

- Approving without reading every changed file.
- Replying "looks good" without specific findings.
- Inventing problems to look thorough — if the diff is clean, say so.

## Why

Source: `/engineering/claude-code-best-practices` — Writer/Reviewer with fresh context is one of the documented effective patterns; the same Claude that wrote the code is biased toward defending it.

Source: `/engineering/multi-agent-research-system` — agents grade end-state better than path; reviewers should evaluate the artifact, not the journey to it.
