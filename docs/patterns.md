# Patterns

Patrones de diseño de agentes documentados en los 24 posts. Cada uno: cuándo usarlo, cuándo no, y cómo cablearlo.

---

## F1. Long-running agents (initializer + coder harness)

**Cuándo usarlo**: tareas que no caben en una sola context window de 200K tokens. Build de aplicaciones de horas/días, migraciones masivas, research multi-día.

**Cuándo NO**: cualquier cosa que cabe en una sesión. Tareas latency-sensitive single-turn.

**Cómo cablearlo**:

1. **Initializer** (corre una vez):
   - Lee el spec.
   - Produce `feature_list.json` con la descomposición en tareas.
   - Produce `init.sh` con el bootstrap del entorno.
   - Hace el commit inicial (baseline limpio).
   - Produce `claude-progress.txt` con la goal y los next 3 actions.

2. **Coder** (corre N veces):
   - Lee `claude-progress.txt`.
   - Toma el siguiente feature de `feature_list.json`.
   - Lo implementa sobre git limpio.
   - Corre verificación (tests, lint).
   - Apendea el progreso a `claude-progress.txt`.
   - Commit.
   - Termina la sesión. Hace `/clear` (o cierra). La siguiente invocación empieza de cero leyendo el archivo.

Mismo modelo, mismo harness, dos system prompts diferentes.

**Versión avanzada (3 roles)** del post `harness-design-long-running-apps`:

- **Planner** — decompone, negocia el "done", produce sprint contracts con grading criteria.
- **Generator** — implementa según el sprint contract.
- **Evaluator** — verifica el sprint contract, no se trata del mismo agente que generó.

Métricas reportadas: solo run = 20 min, $9. Harness v1 = 6 hs, $200. Harness v2 con los 3 roles = 3.8 hs, $124.70. La inversión es 14× costo pero produce código deployable consistentemente, donde el solo run produce código que necesita rework manual.

> Fuente: `/engineering/effective-harnesses-for-long-running-agents`, `/engineering/harness-design-long-running-apps`, `/engineering/building-c-compiler`

---

## F2. Multi-agent (orchestrator + subagents)

**Cuándo usarlo**:
- Investigación breadth-first con dimensiones independientes (research, reviews comparativos, análisis multi-fuente).
- Espacio de búsqueda excede una context window.
- El token usage explica más performance que la "inteligencia" del modelo (Anthropic midió que token usage = 80% de la varianza en BrowseComp).

**Cuándo NO**:
- Coding (acoplamiento entre componentes mata el paralelismo).
- Tareas con estado mutable compartido entre agentes.
- Cuando el costo importa — multi-agent usa **~15×** los tokens de un chat.

**Cómo cablearlo**:

```
┌──────────────────────────────────────┐
│  Lead orchestrator                   │
│  - Decompone pregunta en 3-5 subqs   │
│  - Despacha subagentes en paralelo   │
│  - Sintetiza findings                │
└──────────────────────────────────────┘
        │       │       │
        ▼       ▼       ▼
   ┌────────┬────────┬────────┐
   │ Agent1 │ Agent2 │ Agent3 │
   │ obj X  │ obj Y  │ obj Z  │
   └────────┴────────┴────────┘
        │       │       │
        ▼       ▼       ▼
    findings (1-2K tokens cada uno)
```

**Brief de cada subagente debe incluir TODOS estos**:

| Campo | Ejemplo |
|-------|---------|
| Objective | "Listar las 5 librerías de validación de JSON Schema más usadas en Node ecosystem en 2026, con weekly downloads." |
| Output format | Tabla markdown: nombre, downloads, último release, license. |
| Source guidance | npm registry y GitHub stars. NO usar listicles de Medium. |
| Tool budget | 5-8 calls. |
| Boundaries | NO incluir librerías deprecated. NO incluir TypeScript-only solutions. |

**Métricas reportadas**: orchestrator-worker beat single-agent por 90.2% en eval interno de research. Pero el costo por query es ~15× chat.

> Fuente: `/engineering/multi-agent-research-system`, `/engineering/building-effective-agents`

---

## F3. Context engineering (just-in-time + structured notes)

**Cuándo usarlo**: siempre. No es un patrón de cuándo, es un patrón de cómo.

**Principios**:

1. **Right altitude** en el system prompt — ni hardcoded if/else (brittle), ni vague platitudes (sin signal). Reglas concretas con margen heurístico.

2. **Just-in-time retrieval** — no cargar toda la documentación upfront. Dejar que Claude haga targeted greps/globs cuando necesita. CLAUDE.md tiene punteros (`docs/architecture.md` — léelo cuando necesites entender el sistema), no el contenido completo.

3. **Pocos few-shots canónicos**, no exhaustivos. 3-5 ejemplos diversos > 30 ejemplos parecidos.

4. **Compaction** cuando el contexto se llena (`/compact` built-in).

5. **Structured note-taking** para horizons largos (`claude-progress.txt`, ver patrón F1).

6. **Sub-agent spawning** para exploración paralela (ver F2).

> Fuente: `/engineering/effective-context-engineering-for-ai-agents`

---

## F4. Retrieval (Contextual Retrieval para RAG)

**Cuándo usarlo**: RAG sobre documentos chunkeados donde los chunks pierden significado fuera del contexto del documento — codebases, SEC filings, PDFs largos, documentación técnica.

**Cuándo NO**: documentos suficientemente chicos para caber en context. Stuffear directamente es más simple y más exacto.

**Cómo cablearlo**:

```
Para cada chunk del documento original:
  1. Generar contexto del chunk via Claude
     (50-100 tokens explicando "qué es este chunk
      en relación al documento entero").
  2. Concatenar: <contexto> + <chunk original>.
  3. Embedear el resultado.
  4. Indexar tanto en vector store como en BM25.

Para queries:
  1. Vector search (embeddings) → top K1.
  2. BM25 → top K2.
  3. Reciprocal rank fusion → top K (típicamente 20).
  4. Reranking → top N (típicamente 5-10) que van al LLM.
```

**Métricas reportadas** (de Anthropic):
- Embeddings solos: -35% retrieval failure.
- + BM25: -49%.
- + reranking: -67%.

**Truco de costo**: la generación de contexto por chunk es cara (un LLM call por chunk). Usar prompt caching del documento original hace que el N-ésimo chunk cueste casi nada.

> Fuente: `/engineering/contextual-retrieval`

---

## F5. Think tool (uso restringido)

**Cuándo usarlo**: cadenas largas de tool calls secuenciales, dominios con políticas (airline customer service, compliance, legal). El use case canónico es: tool 1 retorna info A, tool 2 necesita decidir basado en A + policy X — un `think` step entre ambos da +54% relativo en τ-bench airline.

**Cuándo NO**:
- Single tool calls.
- Tool calls paralelos.
- Tareas simples de instruction-following.
- **En general** — la update note del 15-Dec-2025 del post oficial recomienda **extended thinking en lugar del `think` tool en la mayoría de casos**. Extended thinking se invoca con triggers como "think hard" / "ultrathink" en el prompt y es más simple de cablear.

**Cómo cablearlo** (si decidís usarlo):

1. Agregar a la lista de tools del modelo:
```python
{
  "name": "think",
  "description": "Use the tool to think about something. It will not obtain new information or change the database, but just append the thought to the log. Use it when complex reasoning or some cache memory is needed.",
  "input_schema": {
    "type": "object",
    "properties": {
      "thought": { "type": "string", "description": "A thought to think about." }
    },
    "required": ["thought"]
  }
}
```

2. La tool es no-op — no hace nada con el input excepto loggearlo.

3. En el system prompt, dar ejemplos específicos del dominio sobre **qué pensar**: regla a verificar, info a chequear, plan a validar. La guidance larga va en el system prompt, NO en la tool description.

> Fuente: `/engineering/claude-think-tool` (con la update note del 2025-12-15)

---

## F6. Cuándo NO usar agentes

Patrón meta-importante: muchos casos no necesitan un agente. Una pipeline de prompts + retrieval + tools alcanza, sin loop autónomo.

**Workflows ≠ agents**. Un workflow es un grafo determinístico de pasos. Un agente es un loop donde el modelo decide qué hacer próximo. El primer error de muchos teams es agentificar lo que sería más simple, más confiable y más barato como workflow.

**Empezar simple**:
1. Single LLM call. ¿Resuelve el problema? Listo.
2. Agregar retrieval (contextual si los chunks lo justifican). ¿Resuelve? Listo.
3. Agregar tools (con descriptions cuidadas). ¿Resuelve? Listo.
4. Recién acá: workflow multi-step. Pipeline determinística donde cada paso es prompt + tools. ¿Resuelve? Listo.
5. **Solo si lo anterior no alcanza**: agente con loop. Y si vas a un agente, considerá si single-agent o multi-agent (ver F2).

Razón: los agentes amplifican errores. Cada turn introduce probabilidad de equivocarse, y los errores se compounden. Para problemas que un workflow cubre, el workflow gana en costo, latencia y consistencia.

> Fuente: `/engineering/building-effective-agents`

---

## F7. Hardware noise budget (para evals serios)

**Cuándo aplica**: cualquier eval o benchmark donde el resultado va a influenciar decisiones (cambio de modelo, cambio de prompt, claim público).

**Cómo cablearlo**:

1. **Cada task corre N≥3 veces**. Reportar media y std, no point estimate.
2. **Resource cap explícito**: `guaranteed_allocation` Y `hard_kill_threshold` separados, con headroom band (típicamente 3× para que noise no se mezcle con kills reales).
3. **Documentar la config**: si el setup no está publicado, los resultados no son reproducibles.

**Por qué importa**: Anthropic midió 6pp de diferencia (p<0.01) entre setups con resource caps estrictos vs uncapped, en la misma eval, con el mismo modelo. Si tu eval reporta 3pp de diferencia entre dos prompts pero no controlaste por noise, podría ser ruido. Si reporta 8pp, sabés que es signal real.

> Fuente: `/engineering/infrastructure-noise`, `/engineering/multi-agent-research-system`
