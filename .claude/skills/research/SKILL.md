---
name: research
description: Use for breadth-first investigation of a question with multiple independent dimensions. Decomposes into 3-5 subquestions and dispatches parallel subagents. Costs ~15× single-agent tokens — reserve for genuine breadth questions.
---

# /research — multi-agent breadth-first investigation

You are the **lead orchestrator**. Do NOT do the research yourself in this turn — delegate to subagents.

## Procedure

1. **Restate the question**. If it's narrow enough that one Claude could answer it in 3-10 tool calls, abort and tell the user this skill is overkill.
2. **Decompose into 3-5 independent subquestions**. Independence is the key — if subquestion B depends on subquestion A's answer, do them sequentially in one agent, not in parallel.
3. **For each subquestion, brief a subagent** with all of these:
   - **Objective**: one sentence, narrow.
   - **Output format**: structured (JSON, table, bullet list) — never free-form prose.
   - **Source guidance**: which sources are authoritative, which to ignore.
   - **Tool/source budget**: 3-10 calls for fact-finding, 10-15 for comparison. Cap explicitly.
   - **Boundaries**: what NOT to research.
4. **Dispatch the subagents in parallel** using the Task tool (or the equivalent in your environment). Track them.
5. **Each subagent returns** a condensed finding (~1-2K tokens). Do NOT have them dump raw search results into your context.
6. **Synthesize** into `RESEARCH.md` with sections:
   - Executive answer (3-5 sentences).
   - Findings per subquestion (with subagent citations).
   - Contradictions or gaps between subagents.
   - Open questions the research did NOT answer.
7. **Cite sources** inline. Every non-trivial claim needs a URL or document reference.

## When NOT to use this skill

- The question fits in one context window of one Claude.
- The question requires real-time coordination across the agents (multi-agent breaks down with shared mutable state).
- Token cost matters more than breadth — `/research` uses roughly 15× the tokens of a single chat session. (source: `/engineering/multi-agent-research-system`)

## Anti-patterns to refuse

- Spawning 50 subagents for a simple query. Effort scales to query complexity, not to enthusiasm.
- Vague subagent briefs ("research X"). Without objective, format, sources, and boundaries, subagents produce mush.
- Restarting from scratch on every error. Build resumption — note partial progress and continue.

## Why

Source: `/engineering/multi-agent-research-system` — orchestrator-worker beat single-agent by 90.2% on Anthropic's internal eval; token usage explained 80% of variance on BrowseComp. The pattern is documented to work — but only when each subagent gets a precise brief.

Source: `/engineering/eval-awareness-browsecomp` — multi-agent runs had 3.7× higher contamination rate than single-agent (0.87% vs 0.24%) on BrowseComp. For research-style queries this is fine; for evals it's a hazard.
