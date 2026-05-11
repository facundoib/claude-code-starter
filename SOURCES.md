# SOURCES

Tabla de procedencia: posts del blog de Anthropic engineering y recetas del cookbook de la plataforma (platform.claude.com/cookbook), qué dice cada uno, y qué secciones de este repo alimenta.

| # | Post | Fecha | Key takeaway (1 oración) | Alimenta |
|---|------|-------|--------------------------|----------|
| 1 | [april-23-postmortem](https://www.anthropic.com/engineering/april-23-postmortem) | 2026-04-23 | Tres cambios silenciosos al system prompt degradaron Opus 4.6/4.7 en 3pp; sin evals continuas, las regresiones son invisibles hasta las quejas. | PRINCIPLES §5, ANTIPATTERNS A34/A35, eval/SKILL |
| 2 | [managed-agents](https://www.anthropic.com/engineering/managed-agents) | 2026-04-08 | Decoupling brain (harness) de hands (sandboxes) bajó p50 TTFT 60% y p95 90%; credentials van en vault separado del container untrusted. | docs/architecture, docs/tools, ANTIPATTERNS A37 |
| 3 | [claude-code-auto-mode](https://www.anthropic.com/engineering/claude-code-auto-mode) | 2026-03-25 | Auto mode con classifier de 2 etapas baja FPR de 8.5% a 0.4%; documenta 8 attack vectors (overeager, prompt injection, scope escalation, etc.). | QUICKSTART §5, settings.json template, ANTIPATTERNS A15/A16/A17 |
| 4 | [harness-design-long-running-apps](https://www.anthropic.com/engineering/harness-design-long-running-apps) | 2026-03-24 | Generator/evaluator separados + sprint contracts + grading criteria; harness 20× más caro que solo run pero produce código deployable ($9 vs $200). | docs/patterns §F1, plan/SKILL, ANTIPATTERNS A22/A23 |
| 5 | [eval-awareness-browsecomp](https://www.anthropic.com/engineering/eval-awareness-browsecomp) | 2026-03-06 | Multi-agent runs tuvieron 3.7× más contamination rate que single-agent (0.87% vs 0.24%) en BrowseComp; soluciones en plaintext son leak. | research/SKILL, ANTIPATTERNS A29 |
| 6 | [infrastructure-noise](https://www.anthropic.com/engineering/infrastructure-noise) | 2026-02-05 | Setups con resource caps estrictos vs uncapped difieren 6pp (p<0.01); reportar varianza, no solo point estimates. | eval/SKILL, evals/run.py, ANTIPATTERNS A28 |
| 7 | [building-c-compiler](https://www.anthropic.com/engineering/building-c-compiler) | 2026-02-05 | 16 agents paralelos, ~2000 sesiones, $20K, 100K LOC, 99% pass rate; tests "extremely high-quality" como verificadores son la palanca. | tdd/SKILL, compact-resume/SKILL, ANTIPATTERNS A31/A36 |
| 8 | [AI-resistant-technical-evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations) | 2026-01-21 | 50%+ de candidatos quedaban mejor delegando a Sonnet 3.7 que resolviendo solos; problemas novel/out-of-distribution + tiempo libre revelan signal real. | docs/patterns, eval/SKILL |
| 9 | [demystifying-evals-for-ai-agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | 2026-01-09 | Empezar con 20-50 tareas de fallas reales; balanced sets; reference solutions; LLM judges con rúbrica única; equipos dedicados. | eval/SKILL, ANTIPATTERNS A24/A25/A26/A27, evals/judge.py |
| 10 | [effective-harnesses-for-long-running-agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | 2025-11-26 | Harness de dos agentes (initializer + coder) con `claude-progress.txt` permite trabajar a través de muchas context windows. | compact-resume/SKILL, docs/patterns §F1 |
| 11 | [advanced-tool-use](https://www.anthropic.com/engineering/advanced-tool-use) | 2025-11-24 | Tres betas (Tool Search Tool, Programmatic Tool Calling, Tool Use Examples) atacan context bloat / intermediate result pollution / parameter ambiguity. | docs/tools, ANTIPATTERNS A4 |
| 12 | [code-execution-with-mcp](https://www.anthropic.com/engineering/code-execution-with-mcp) | 2025-11-04 | Presentar MCPs como código callable cortó token spend Drive→Salesforce de 150K a 2K (98.7% saving). | docs/tools, ANTIPATTERNS A4 |
| 13 | [claude-code-sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing) | 2025-10-20 | Filesystem + network isolation reducen 84% prompts de permisos; ambos límites son requeridos. | QUICKSTART §4, settings.json template (sandbox), ANTIPATTERNS A11/A12/A13 |
| 14 | [equipping-agents-for-the-real-world-with-agent-skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | 2025-10-16 | Skills = folders con `SKILL.md` (frontmatter `name` + `description`); progressive disclosure carga solo metadata upfront. | .claude/skills/*, PRINCIPLES §4 |
| 15 | [effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 2025-09-29 | Contexto es presupuesto finito; encontrar el menor set de tokens high-signal vía right-altitude prompts, just-in-time retrieval, compaction, note-taking. | CLAUDE.md template, PRINCIPLES §1, ANTIPATTERNS A1/A2/A3 |
| 16 | [a-postmortem-of-three-recent-issues](https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues) | 2025-09-17 | Tres issues afectaron 0.8-16% de requests; root causes invisibles a evals ruidosas; necesidad de evals que diferencien working vs broken. | eval/SKILL, ANTIPATTERNS A28 |
| 17 | [writing-tools-for-agents](https://www.anthropic.com/engineering/writing-tools-for-agents) | 2025-09-11 | Tools deben consolidar workflows, namespace cleanly, devolver semantic IDs, exponer `concise|detailed`, validarse con held-out tests. | docs/tools, ANTIPATTERNS A5/A6/A7/A8/A9 |
| 18 | [desktop-extensions](https://www.anthropic.com/engineering/desktop-extensions) | 2025-06-26 | `.mcpb` bundles un MCP server + deps + manifest en one-click install; secrets vía `sensitive: true` van al OS keychain. | docs/tools, ANTIPATTERNS A32/A33 |
| 19 | [multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system) | 2025-06-13 | Orchestrator-worker le ganó al single-agent por 90.2% en eval interno; multi-agent usa ~15× tokens de chat. | research/SKILL, docs/patterns §F2, ANTIPATTERNS A18/A19/A20/A21 |
| 20 | [claude-code-best-practices](https://www.anthropic.com/engineering/claude-code-best-practices) | 2025-04-18 | Recipe canónica: CLAUDE.md, explore → plan → code → commit, course-correct early, sandboxed shell, headless `claude -p` para batch. | README, QUICKSTART, CLAUDE.md template, plan/SKILL, tdd/SKILL, review/SKILL, PRINCIPLES |
| 21 | [claude-think-tool](https://www.anthropic.com/engineering/claude-think-tool) | 2025-03-20 | `think` tool gives +54% relative en τ-bench airline; **update Dec 2025**: Anthropic recomienda extended thinking en lugar de `think` tool en la mayoría de casos. | docs/patterns §F5 |
| 22 | [swe-bench-sonnet](https://www.anthropic.com/engineering/swe-bench-sonnet) | 2025-01-06 | Bash + Edit (con `old_str`/`new_str` exact match único) + 200K context + scaffolding mínimo = 49% en SWE-bench Verified. | docs/tools, ANTIPATTERNS A30 |
| 23 | [building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents) | 2024-12-19 | Workflows ≠ agents; empezar simple (single LLM + retrieval + tools), agregar agentic patterns solo cuando la complejidad lo demanda. | docs/patterns, PRINCIPLES §8 |
| 24 | [contextual-retrieval](https://www.anthropic.com/engineering/contextual-retrieval) | 2024-09-19 | Prepend chunk-context generado por Claude antes de embedear; +BM25 +reranking juntos cortan retrieval failure 67%. Use prompt caching para hacerlo viable. | docs/patterns §F4 |
| 25 | [context-engineering-tools](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools) | 2026-03 | Clearing > compaction cuando los tool results dominan el contexto: clearing cuesta zero inferencia y da 67% reducción (128K→43K tokens); compaction cuesta un call y da ~50%. En un run de referencia, file-read results = 96.3% del contexto total. | docs/patterns §F3, ANTIPATTERNS A38 |
| 26 | [tool-evaluation](https://platform.claude.com/cookbook/tool-evaluation-tool-evaluation) | 2025-09 | Tool schema sin documentar operaciones soportadas fuerza a Claude a inventar workarounds: sin `log10()` documentado, la tarea de pH tomó 16 tool calls vs 1-7 con schema documentado; 87.5% accuracy en suite de 8 tareas, 22.73s avg por tarea. | docs/tools Pattern 6, ANTIPATTERNS A9 |

---

## Cómo se actualiza esta tabla

Cuando Anthropic publica un post nuevo en `/engineering/` o una receta nueva en `platform.claude.com/cookbook`, se evalúa contra estos criterios:

- ¿Trae una recomendación accionable? Si no (puro postmortem sin lecciones forward-looking), no entra.
- ¿La recomendación contradice o supera alguna existente? Si sí, actualizar la sección afectada y marcar el post anterior como superseded.
- ¿Hay claims numéricos? Citarlos con la métrica exacta del post, no parafrasear.

PRs para agregar posts nuevos van con: link al post, fecha, takeaway en una oración, y mapeo a sección(es) del repo.

---

## Fuentes consideradas pero excluidas

### Entradas del cookbook — primera pasada, mayo 2026

De 7 entradas evaluadas, 5 se excluyeron:

| Entrada | Razón |
|---|---|
| Outcomes: Agents That Verify Their Own Work | Claude Managed Agents product-specific (`client.beta.sessions.events.send`); no aplica a Claude Code CLI |
| Session Memory Compaction | Audiencia API/SDK; el patrón de background threading no mapea al `compact-resume/SKILL` de Claude Code CLI |
| Basic Workflows | Cubierto por post #23 (building-effective-agents) con mayor profundidad y métricas duras |
| Evaluator Optimizer | Cubierto por post #4 (harness-design) con métricas cuantitativas ($9 vs $200) que el cookbook no aporta |
| Orchestrator Workers | Cubierto por posts #19 y #23; no agrega sobre `docs/patterns §F2` |

### Posts del blog de engineering

Ninguno excluido — los 24 posts del hub al momento de la curaduría inicial entraron todos. Si en el futuro algún post resulta no aplicable (ej. demasiado específico a un producto Anthropic interno), se documenta acá.
