# Tools y MCP

Cómo elegir, escribir y configurar tools (custom + MCP) para que un agente las use bien. Todo desde lo que dicen los posts.

---

## Cuántos MCPs instalar (spoiler: pocos)

El failure mode documentado: "bloated tool sets que cubren demasiada funcionalidad o tienen ambiguous decision points". Anthropic midió 134K tokens consumidos solo por tool definitions en un setup interno — eso es atención perdida antes de empezar la tarea.

**Recomendación**: 3-5 MCPs que vas a usar a diario, no más.

**Starter set típico**:
- GitHub — issues, PRs, repos.
- Tu sistema de tickets (Linear, Jira) — si trabajás con uno.
- Una BD si hacés SQL ad-hoc (Postgres MCP, Supabase MCP).
- (Opcional) Notion / Confluence si tu doc vive ahí.

**Lo que NO hacés**:
- Instalar todo lo del marketplace "por las dudas".
- Wrappear cada SaaS interno como MCP "porque podemos".

> Fuente: `/engineering/writing-tools-for-agents`, `/engineering/advanced-tool-use`

---

## Cómo distribuir MCPs (Desktop Extensions / `.mcpb`)

Cuando publicás un MCP server, prefiero `.mcpb` (Desktop Extensions) sobre el setup manual de `claude_desktop_config.json`. Razones:

- One-click install para el usuario final.
- Dependencies bundleadas — no hay "instalá Node 20 antes de continuar".
- Secrets vía `sensitive: true` en el manifest van al OS keychain, no a un JSON plaintext.
- `user_config` declarado en el manifest evita que el usuario tenga que editar JSON.

> Fuente: `/engineering/desktop-extensions`

> **Nota**: este claim sobre `.mcpb` específicamente requiere verificación adicional contra docs vigentes — al momento de la curaduría, no se pudo confirmar el formato exacto en `code.claude.com/docs`. La forma del manifest descripta acá viene del post de Anthropic; revisar antes de adoptarlo en producción.

---

## Patrones para tool design (custom o MCP)

### Pattern 1: una tool por workflow, no por endpoint

**Mal**:
```
list_users(filters)
list_events(user_id)
create_event(user_id, time, data)
```

Tres calls para programar una reunión. Cada call es chance de error y consume contexto.

**Bien**:
```
schedule_meeting(participants, time, agenda)
```

Una call, un workflow consolidado. Internamente la tool hace los 3 lookups, pero Claude solo ve el workflow.

> Fuente: `/engineering/writing-tools-for-agents`

### Pattern 2: identificadores semánticos sobre UUIDs

**Mal**: `{"user_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"}`
**Bien**: `{"username": "alice@example.com"}`

Claude tiene mejor recall sobre slugs/usernames que sobre UUIDs aleatorios. Si tu API expone ambos, devolvé el semántico.

> Fuente: `/engineering/writing-tools-for-agents`

### Pattern 3: errores accionables, no stack traces

**Mal**:
```json
{ "error": "ValidationError: status invalid" }
```

**Bien**:
```json
{
  "error": "Invalid status 'Pending'",
  "valid_options": ["pending", "shipped", "delivered"],
  "hint": "Status values are lowercase. Did you mean 'pending'?"
}
```

Claude puede recuperarse de un error que entiende. No puede recuperarse de uno opaco.

> Fuente: `/engineering/writing-tools-for-agents`

### Pattern 4: response_format con enum `concise|detailed`

Si tu tool puede devolver mucha data, exponé un parámetro:

```json
{
  "name": "get_record",
  "input_schema": {
    "properties": {
      "id": { "type": "string" },
      "response_format": {
        "type": "string",
        "enum": ["concise", "detailed"],
        "default": "concise"
      }
    }
  }
}
```

`concise` devuelve los 3-5 campos críticos. `detailed` devuelve todo. Claude elige según necesidad. Sin esto, devolvés siempre el detalle y contaminás contexto.

> Fuente: `/engineering/writing-tools-for-agents`

### Pattern 5: truncar listas con mensaje útil

Tools que devuelven listas: cap a ~25K tokens. Si hay más, devolver un mensaje explícito:

```json
{
  "results": [...],
  "truncated": true,
  "total_count": 12500,
  "shown_count": 50,
  "hint": "Add filter `created_after` or use pagination (cursor: <opaque>) to narrow."
}
```

Claude Code aplica esto en sus tools internas por default.

> Fuente: `/engineering/writing-tools-for-agents`

### Pattern 6: tool descriptions como onboarding doc

La description de una tool se carga en cada turn. Es un prompt persistente. Editarla con el mismo cuidado que un system prompt.

**Mal**:
> "Returns user data."

**Bien**:
> "Returns the user's profile, recent activity, and team memberships. Returns null fields for any data the requester is not authorized to see — check the `permissions` field in the response. IDs follow format `usr_<10 alphanumeric>`. For batch lookup, prefer `get_users_batch` (max 50 IDs per call)."

Formats explícitos, ID schemes explícitos, pointers a tools relacionadas. Documentar también **qué operaciones soporta** la tool: una calculadora sin `log10()`, `sqrt()`, `round()` declarados forzó 16 tool calls para una tarea de pH (workarounds hardcoded como `**0.5` para raíz cuadrada). Con documentación completa, tareas equivalentes tomaron 1-7 calls.

> Fuente: `/engineering/writing-tools-for-agents`, `/engineering/swe-bench-sonnet`, `cookbook/tool-evaluation`

### Pattern 7: input_examples para tools con schema complejo

Cuando una tool tiene parámetros opcionales no obvios o objetos anidados, agregar `input_examples`:

```json
{
  "name": "create_event",
  "input_schema": { ... },
  "input_examples": [
    {
      "title": "Standup",
      "start": "2026-05-09T10:00:00Z",
      "duration_minutes": 15,
      "participants": ["alice@x.com"]
    },
    {
      "title": "Quarterly review",
      "start": "2026-06-01T14:00:00Z",
      "duration_minutes": 60,
      "participants": ["alice@x.com", "bob@x.com"],
      "recurring": { "frequency": "quarterly", "count": 4 }
    }
  ]
}
```

Los ejemplos resuelven ambigüedades que ni la mejor description elimina.

> Fuente: `/engineering/advanced-tool-use`

---

## Setups avanzados

### Tool Search Tool (cuando tenés muchas tools)

Si tu setup tiene ≥10 tools o las definitions superan ~10K tokens, usar `defer_loading: true`:

```json
{
  "tools": [
    { "name": "search_tools", "description": "..." },
    { "name": "github_create_pr", "defer_loading": true, "..." },
    { "name": "linear_create_issue", "defer_loading": true, "..." },
    ...
  ]
}
```

Claude empieza con solo `search_tools` cargada (más unas pocas core). Cuando necesita una tool específica, la busca y la carga on-demand.

> Fuente: `/engineering/advanced-tool-use`

### Programmatic Tool Calling (Code Mode)

Para workflows con 3+ calls dependientes y data intermedia grande, exponer las tools como funciones callables desde un Python REPL en lugar de tool calls directas:

- Antes: 5 tool calls, cada uno con I/O en el contexto del modelo (potencialmente 100K+ tokens).
- Después: 1 tool call con un script Python que orquesta los 5; el modelo solo ve el resultado final (típicamente <2K tokens).

Métrica del post: workflow Drive→Salesforce bajó de 150K a 2K tokens (98.7% saving).

> Fuente: `/engineering/code-execution-with-mcp`, `/engineering/advanced-tool-use`

### Code Execution con `allowed_callers`

Cuando exponés una tool como callable desde código, podés restringir quién la puede llamar:

```json
{
  "name": "send_email",
  "allowed_callers": ["python_sandbox"]
}
```

Eso permite que un agente la invoque indirectamente (vía un script en Python sandbox), pero no que el modelo la invoque directamente como tool call. Reduce surface de prompt injection.

> Fuente: `/engineering/advanced-tool-use`

---

## File-edit tools (lección del SWE-bench)

El setup de Anthropic que llegó a 49% en SWE-bench Verified usaba dos tools mínimas:

- **Bash** — con paths absolutos, sin cwd ambiguo.
- **Edit** — con `old_str` y `new_str`. **El `old_str` debe matchear EXACTAMENTE UN lugar en el archivo**. Si matchea cero o múltiples, error explícito.

Esa tercera regla es la importante. Edits sobre matches ambiguos son la fuente principal de "Claude editó el archivo equivocado". Si escribís tus propias file-edit tools, replicá esa restricción.

> Fuente: `/engineering/swe-bench-sonnet`

---

## Validación: held-out test sets para tools

Antes de deployar una tool nueva, correrla contra un test set:

1. 10-20 prompts realistas que requieren la tool.
2. Verificar:
   - ¿Claude la invoca cuando debe?
   - ¿No la invoca cuando no debe (false positive)?
   - ¿Maneja errores de la tool sin retry-loop?
   - ¿El output que produce es correcto end-to-end?

Si tu tool tiene una description nueva, este test set es lo único que te dice si la description funciona. Vibes no cuentan.

> Fuente: `/engineering/writing-tools-for-agents`, `/engineering/demystifying-evals-for-ai-agents`
