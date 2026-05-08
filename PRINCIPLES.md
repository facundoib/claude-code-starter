# PRINCIPLES

El por qué de cada decisión del repo. Si discrepás con alguno, el motivo estará en alguno de los 24 posts citados — léelo antes de descartar el principio.

---

## 1. CLAUDE.md como contexto persistente, corto y enforceable

Claude Code carga `CLAUDE.md` en cada sesión automáticamente. Eso significa que cada token ahí cuesta atención del modelo en *cada* turno. La tentación es escribir un manual exhaustivo. La práctica documentada es lo opuesto: corto, específico, enforceable.

- *Específico* gana sobre *vago*: "No `any` en TypeScript, usar `unknown` y narrow" supera a "escribí buen TS".
- *Enforceable* gana sobre *aspiracional*: si no podés verificar que se cumple, no va.
- Tres a cinco secciones, no diez. Las secciones no usadas igual cuestan tokens.

> Fuente: `/engineering/claude-code-best-practices`, `/engineering/effective-context-engineering-for-ai-agents`

---

## 2. Permisos explícitos, no aprobación manual constante

Aprobar cada bash command rompe el flujo y entrena al usuario a aprobar sin leer ("approval fatigue"). El research interno de Anthropic muestra que los usuarios aprueban el 93% de los prompts de permisos — la fricción no compra seguridad real.

La alternativa documentada: definir el allowlist y denylist explícitamente en `.claude/settings.json`. Lo que no esté en allow se prompta. Lo que esté en deny nunca corre.

> Fuente: `/engineering/claude-code-sandboxing`, `/engineering/claude-code-auto-mode`

---

## 3. Sandbox con doble límite (filesystem + red), no uno solo

Aislar solo filesystem deja que Claude exfiltre contenido vía `curl`. Aislar solo red deja que Claude lea `~/.ssh/id_rsa`. Anthropic es explícito: "sandboxing efectivo requiere *ambos* límites".

- Filesystem: `allowRead`/`allowWrite`/`denyRead`/`denyWrite` con paths específicos.
- Red: `allowedDomains` con whitelist de hosts; bloqueo implícito del resto.

El resultado interno medido fue **84% menos prompts de permisos** sin pérdida de seguridad.

> Fuente: `/engineering/claude-code-sandboxing`

---

## 4. Skills en `.claude/skills/`, no `.claude/commands/`

Los slash commands legacy (`.claude/commands/<name>.md`) siguen funcionando, pero Anthropic los unificó con skills. La diferencia operativa: skills usan **progressive disclosure** — solo el frontmatter (`name`, `description`) se carga upfront; el body se expande on-demand cuando Claude decide invocarla.

Eso permite tener decenas de skills sin saturar contexto. Los commands legacy cargaban el cuerpo completo siempre.

> Fuente: `/engineering/equipping-agents-for-the-real-world-with-agent-skills`

---

## 5. Evals desde el día 1, con 20 tareas, no 200

Las evals tienden a postergarse hasta tener "suficientes" casos. Anthropic empezó cada una de sus suites internas con 20-50 tareas extraídas de fallas reales, no de casos hipotéticos.

Razón concreta: el incidente de abril 2026 (Anthropic propio) — un cambio de "verbosity instruction" en el system prompt degradó 3pp los evals de Opus 4.6 y 4.7. Sin eval suite continua, las regresiones se detectan recién cuando los usuarios se quejan.

Reglas clave para que las evals funcionen:
- Cada tarea corre **3+ veces** y se reporta media + varianza (los agentes son no-determinísticos).
- LLM-as-judge con **una sola rúbrica y un solo score 0.0-1.0** por llamada — múltiples rúbricas en una sola call introducen ruido.
- Verificá end-state, no path. Que el código corra y los tests pasen, no que Claude haya seguido los pasos exactos que vos imaginaste.

> Fuente: `/engineering/demystifying-evals-for-ai-agents`, `/engineering/multi-agent-research-system`, `/engineering/april-23-postmortem`, `/engineering/infrastructure-noise`

---

## 6. TDD como contract de "hecho", no como filosofía

Tests no son una creencia religiosa, son el único objeto verificable. Claude puede convencerte de que el código funciona; los tests no se dejan convencer.

El build del compilador de C en Anthropic (16 agentes paralelos, ~2000 sesiones, 100K LOC, $20K) usó tests "extremadamente high-quality" como verificadores de tarea. Sin esos tests, ningún harness multi-agente escala — los agentes se auto-engañan sobre el estado de "completado".

> Fuente: `/engineering/building-c-compiler`, `/engineering/claude-code-best-practices`

---

## 7. Review con contexto fresco, no auto-review

El mismo Claude que escribió el código está sesgado a defenderlo. La práctica documentada: abrir una sesión nueva sin contexto previo, alimentarle solo el diff y el spec, y pedir crítica.

Análogo humano: code review por alguien que no participó del PR. La diferencia es que con Claude es trivialmente barato hacer esto — un `/clear` + un nuevo prompt y tenés un revisor sin sesgo.

> Fuente: `/engineering/claude-code-best-practices`

---

## 8. Multi-agent solo para breadth real, no para todo

El sistema multi-agent de Anthropic le ganó al single-agent por **90.2%** en su eval interno. Pero usa **~15× los tokens** de un chat. Para tareas de breadth genuino (research con dimensiones independientes), el costo se justifica. Para coding o tareas con estado mutable compartido, single-agent es estrictamente mejor hoy.

Triggers para usar `/research`:
- La pregunta tiene 3+ dimensiones independientes que pueden investigarse en paralelo.
- El espacio de búsqueda excede una sola context window.
- Los hallazgos individuales son condensables (10K → 1-2K tokens) antes de la síntesis.

Triggers para NO usarlo:
- Tareas de coding (acoplamiento entre componentes mata el paralelismo).
- Tareas con estado mutable compartido entre agentes.
- Cuando el costo en tokens importa más que la cobertura.

> Fuente: `/engineering/multi-agent-research-system`, `/engineering/building-effective-agents`

---

## 9. `claude-progress.txt` para sesiones largas, no compaction sola

Compaction reduce contexto pero conserva la sesión. Para tareas multi-hora o multi-día, eso no alcanza — hay un fenómeno de "context anxiety" donde el modelo tira referencias a turnos viejos que ya no son load-bearing.

El patrón documentado: escribir progreso estructurado a `claude-progress.txt`, hacer `/clear` completo, y arrancar una sesión nueva que lee el progreso. La estructura (Goal / Completed / In progress / Open decisions / Next actions / Files of interest / Anti-patterns to remember) es la del harness de larga duración de Anthropic.

> Fuente: `/engineering/effective-harnesses-for-long-running-agents`, `/engineering/harness-design-long-running-apps`

---

## 10. Plan antes de código, con presupuesto explícito de razonamiento

Saltar de prompt a código sin pasar por un plan es la receta documentada para la mayor fuente de rework. El ciclo canónico:

1. **Explore** — Claude lee archivos relevantes, sin escribir código.
2. **Plan** — produce `PLAN.md` numerado, con riesgos y archivos a tocar.
3. **Code** — implementa siguiendo el plan.
4. **Commit** — chico, descriptivo.

Para presupuesto extra de razonamiento en planes complejos, Claude responde a triggers de extended thinking ("think hard", "ultrathink"). El extra de tokens en el plan se paga muchas veces con el ahorro en re-implementación.

> Fuente: `/engineering/claude-code-best-practices`, `/engineering/effective-context-engineering-for-ai-agents`

---

## 11. Tools que consolidan workflows, no que envuelven endpoints

Cuando exponés tools a Claude (custom o vía MCP), la tentación es mapear 1:1 con la API subyacente. La práctica documentada lo desaconseja: si Claude tiene que llamar `list_users` + `list_events` + `create_event` para agendar una reunión, perdés contexto y aumentás el chance de error en cada hop.

Mejor: una tool `schedule_meeting(participants, time, agenda)` que internamente hace los tres calls. Un tool por workflow, no por endpoint.

Reglas adicionales documentadas:
- Tool descriptions se escriben como onboarding doc para un nuevo hire — explícitas, con formatos y ejemplos.
- Identificadores semánticos (slugs, names) sobre UUIDs — Claude tiene mejor recall sobre los primeros.
- Errores accionables ("intentá uno de: pending|shipped|delivered") sobre stack traces.
- Truncar respuestas a ~25K tokens con un mensaje "usá paginación o filtros".

> Fuente: `/engineering/writing-tools-for-agents`, `/engineering/swe-bench-sonnet`, `/engineering/advanced-tool-use`

---

## 12. Modelo por tarea, no Opus para todo

Anthropic publica tres modelos por una razón: las tareas tienen diferentes costos óptimos. Para el harness de evals de este repo:

- **Sonnet 4.6** — workhorse para coding, refactor, agentic loops. Default razonable.
- **Opus 4.7** — razonamiento profundo, planes complejos, debugging difícil. Reservar.
- **Haiku 4.5** — clasificación, judges simples, tareas one-shot de bajo costo.

El research del C compiler usó modelos diferentes para roles diferentes (un Opus orquestador, varios Sonnet ejecutores). El patrón se replica acá si vas a multi-agent.

> Fuente: `/engineering/building-c-compiler`, `/engineering/managed-agents`

---

## Cierre

Los principios anteriores no son opiniones — cada uno cita el post de Anthropic que lo respalda. Si encontrás un caso donde el principio falla en tu contexto, es información interesante: o el contexto es suficientemente distinto del de Anthropic para que la transferencia rompa, o el principio cambió en un post posterior. Abrí un issue con el caso y la cita.
