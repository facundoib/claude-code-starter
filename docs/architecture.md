# Architecture: cómo encajan settings, hooks, skills y sandbox

Diagrama mental de las cuatro capas de configuración de Claude Code y cómo interactúan en una sesión.

```
┌────────────────────────────────────────────────────────────────┐
│  Sesión de Claude Code                                         │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CLAUDE.md (project root)  ←  contexto persistente       │  │
│  │  + ~/.claude/CLAUDE.md     ←  preferencias personales    │  │
│  │                                                          │  │
│  │  Cargado automáticamente en cada sesión.                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  .claude/skills/<name>/SKILL.md                          │  │
│  │                                                          │  │
│  │  Solo el frontmatter (name, description) se carga        │  │
│  │  upfront. El body se expande on-demand cuando Claude     │  │
│  │  decide invocar la skill (progressive disclosure).       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Cuando Claude quiere ejecutar una tool (Bash, Edit, …)  │  │
│  │                                                          │  │
│  │  1. ¿Está en .claude/settings.json `permissions.deny`?   │  │
│  │     Sí → bloqueado, sin pregunta.                        │  │
│  │  2. ¿Está en `permissions.allow`?                        │  │
│  │     Sí → ejecuta directo (sin permission prompt).        │  │
│  │  3. Si no:                                               │  │
│  │     - En modo `default`: prompt al usuario.              │  │
│  │     - En modo `auto`: classifier decide (allow/prompt/   │  │
│  │       deny) basado en `autoMode` config.                 │  │
│  │                                                          │  │
│  │  4. PreToolUse hooks corren ANTES de la ejecución.       │  │
│  │     Si retornan exit code != 0, bloquean la ejecución.   │  │
│  │  5. La tool ejecuta en el sandbox configurado en         │  │
│  │     `settings.json::sandbox`. Filesystem y red están     │  │
│  │     limitados según la whitelist/blacklist.              │  │
│  │  6. PostToolUse hooks corren DESPUÉS, sin poder bloquear │  │
│  │     pero sí accionar (lint, notificación, etc).          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Capa 1: CLAUDE.md (contexto persistente)

**Ubicación**: `<repo>/CLAUDE.md` (proyecto) y `~/.claude/CLAUDE.md` (personal/global).

**Cuándo se carga**: en cada sesión de Claude Code, automáticamente.

**Qué va acá**:
- Stack del proyecto, comandos relevantes, convenciones específicas, anti-patrones del repo.
- Lo que Claude necesita saber siempre, no solo en una task específica.

**Qué NO va acá**:
- Documentación exhaustiva de cada función — eso es lo que el código y los tests representan.
- Reglas que cambian frecuentemente — irían en un PLAN.md o en un mensaje de turno.
- Casos exhaustivos — preferí 3-5 ejemplos canónicos.

> Fuente: `/engineering/claude-code-best-practices`, `/engineering/effective-context-engineering-for-ai-agents`

---

## Capa 2: Skills (`.claude/skills/<name>/SKILL.md`)

**Ubicación**: `.claude/skills/<name>/SKILL.md`. El nombre del directorio = nombre de la skill (a menos que el frontmatter `name` lo override).

**Frontmatter obligatorio** (mínimo `description`):

```yaml
---
name: my-skill
description: Use when X happens. Does Y.
---
```

**Cuándo se carga**: el frontmatter se carga upfront en la sesión. El body se expande SOLO cuando Claude decide invocar la skill (porque el contexto matchea la `description`, o porque el usuario tipeó `/<name>` explícitamente).

**Qué va en el body**:
- Instrucciones imperativas a Claude para ejecutar la skill.
- Procedure paso a paso.
- When to use / when NOT to use.
- Anti-patrones a rechazar.

**Subdirectorios opcionales**:
- `scripts/` — scripts ejecutables que la skill puede invocar.
- `references/` — material de referencia que la skill puede leer on-demand.

**Compatibilidad legacy**: `.claude/commands/<name>.md` sigue funcionando, pero skills es el formato recomendado actual.

> Fuente: `/engineering/equipping-agents-for-the-real-world-with-agent-skills`

---

## Capa 3: settings.json (permissions, hooks, sandbox)

**Ubicación**: `.claude/settings.json` (proyecto, committeado y compartido). También existen `~/.claude/settings.json` (user-global) y `.claude/settings.local.json` (proyecto-local, gitignored).

**Tres bloques principales**:

### `permissions`

```json
{
  "permissions": {
    "allow": [ "Bash(npm test)", "Read(./**)", "Edit(./src/**)" ],
    "deny":  [ "Bash(rm -rf *)", "Read(./.env*)" ]
  }
}
```

- `Bash(<comando>)` — comando exacto, o con `*` como wildcard en cualquier posición.
- `Read(<path-pattern>)` y `Edit(<path-pattern>)` — patterns gitignore-style. Soportan `//` (absoluto), `~/` (home), `/` (project-relative), `./` (cwd-relative).
- `deny` gana sobre `allow` cuando hay overlap.
- Lo que no está en allow ni en deny: prompt al usuario en modo default; classifier en modo auto.

### `hooks`

Estructura **anidada** (importante — el research inicial tenía esto mal):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "npm run lint", "timeout": 30 }
        ]
      }
    ]
  }
}
```

Notar:
- El nivel exterior es el evento (`PostToolUse`, `PreToolUse`, `SessionStart`, etc).
- El nivel `matcher` selecciona a qué tools/eventos aplica.
- El nivel interior `hooks` es un array de handlers, cada uno con `type` (puede ser `command`, `http`, `mcp_tool`, `prompt`, `agent`).

Eventos disponibles incluyen: `SessionStart`, `SessionEnd`, `Setup`, `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `StopFailure`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `PermissionRequest`, `PermissionDenied`, `Notification`, `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`.

### `sandbox`

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "allowRead":  ["./", "~/.cache"],
      "allowWrite": ["./"],
      "denyRead":   ["~/.ssh", "~/.aws", "~/.gnupg"],
      "denyWrite":  ["~/.ssh", "~/.aws", "~/.gnupg"]
    },
    "network": {
      "allowedDomains": ["github.com", "registry.npmjs.org"],
      "deniedDomains":  ["sensitive.example.com"],
      "allowUnixSockets": ["~/.ssh/agent-socket"],
      "allowLocalBinding": true
    }
  }
}
```

Notar:
- Keys en **camelCase** (`allowRead`/`allowWrite`/`denyRead`/`denyWrite`/`allowedDomains`/`deniedDomains`). Snake_case no funciona.
- Filesystem y red son independientes — cada uno con su propia whitelist y blacklist.
- Anthropic explícito: ambos límites son necesarios. Filesystem solo permite exfiltración por `curl`; red sola permite leer credentials del filesystem.

> Fuente: `/engineering/claude-code-sandboxing`, `code.claude.com/docs/en/settings.md`

---

## Capa 4: Modo de permisos (`default` vs `auto`)

**Cómo se setea**:
- Por sesión: `claude --permission-mode auto`.
- Por defecto en el repo: `"defaultMode": "auto"` en `.claude/settings.json`.

**`default`** (modo conservador):
- Lo que está en allowlist se ejecuta sin prompt.
- Lo que está en denylist se bloquea sin prompt.
- Todo lo demás: prompt al usuario.
- Útil para proyectos críticos / sensibles.

**`auto`** (autonomous mode):
- Allowlist y denylist como antes.
- Todo lo demás pasa por un classifier de dos etapas.
- El classifier consulta el `autoMode.environment` config (por ejemplo, "Source control: github.example.com/myorg") para decidir.
- Métricas: FPR baja de 8.5% a 0.4%; FNR de "overeager" sube de 6.6% a 17% (tradeoff documentado, ver el post).
- Triggers de escalación: 3 denials consecutivos o 20 totales en una sesión bajan a default.

**`autoMode` config** (necesario en auto mode):

```json
{
  "autoMode": {
    "environment": [
      "$defaults",
      "Source control: github.com/yourorg"
    ],
    "allow": [ "Bash(npm install *)" ],
    "soft_deny": [ "Bash(git push origin main)" ]
  }
}
```

> Fuente: `/engineering/claude-code-auto-mode`, `code.claude.com/docs/en/permission-modes.md`

---

## Cómo interactúan las 4 capas en una sesión típica

1. Claude Code arranca: lee `~/.claude/CLAUDE.md` y `<repo>/CLAUDE.md` → contexto persistente.
2. Lee `.claude/settings.json` → permissions, hooks, sandbox, default mode.
3. Lee `.claude/skills/*/SKILL.md` → solo frontmatter de cada skill.
4. Usuario tipea un mensaje. Claude planea y decide hacer una tool call.
5. Si Claude detecta que una skill aplica (matcheando `description`), expande su body y la sigue. O el usuario tipea `/<skill-name>` directo.
6. Cada tool call pasa por: deny check → allow check → permission mode → PreToolUse hooks → ejecución en sandbox → PostToolUse hooks.
7. La tool produce output. Va al contexto de Claude.

Cada capa es independiente — podés tener CLAUDE.md sin skills, settings sin sandbox, etc. Pero las cuatro juntas son lo que da el setup completo.

> Fuente: integración derivada de los posts citados arriba.
