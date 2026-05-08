# QUICKSTART

Quince pasos para tener Claude Code configurado de forma optimizada en tu proyecto. Sin texto de relleno entre los pasos: si necesitás el por qué de cada uno, está en [PRINCIPLES.md](PRINCIPLES.md).

> **Asunción**: Claude Code ya está instalado y autenticado (`claude` corre en una terminal sin pedir login).

---

## 1. Crear `CLAUDE.md` en la raíz de tu proyecto

Copiar [`templates/CLAUDE.md`](templates/CLAUDE.md) a la raíz de tu repo y editar las secciones marcadas con `<...>`. Claude Code lo carga automáticamente en cada sesión como contexto persistente del proyecto. Mantenelo corto: cada token compite por la atención del modelo.

> Fuente: `/engineering/claude-code-best-practices`, `/engineering/effective-context-engineering-for-ai-agents`

## 2. Crear `~/.claude/CLAUDE.md` para preferencias personales

Tres a cinco líneas con cosas que valen para todos tus proyectos: idioma de commits, convenciones de naming, nivel de verbosidad. Ejemplo:

```markdown
- Commits en español, imperativo, sin emojis.
- Preferir TypeScript sobre JavaScript.
- No hacer refactors no pedidos.
```

> Fuente: `/engineering/claude-code-best-practices`

## 3. Copiar `.claude/settings.json` al proyecto

Copiar [`templates/settings.json`](templates/settings.json) a `.claude/settings.json` en la raíz de tu proyecto. Editar los globs de `permissions.allow` para que reflejen tu stack (cambiar `npm` por `cargo`, `pnpm`, etc. según corresponda). Este archivo se commitea — es config compartida del equipo.

> Fuente: `/engineering/claude-code-best-practices`

## 4. Activar sandbox

Dentro de Claude Code, ejecutar:

```
/sandbox
```

Elegir el modo que corresponda. Sandboxing combina aislamiento de filesystem y de red — los dos límites son necesarios. Anthropic reportó una reducción del 84% de prompts de permisos en su uso interno.

> Fuente: `/engineering/claude-code-sandboxing`

## 5. (Opcional) Activar auto mode para sesiones autónomas largas

Si vas a correr Claude sin supervisión continua, agregar a `.claude/settings.json`:

```json
{
  "defaultMode": "auto"
}
```

O invocar como flag por sesión: `claude --permission-mode auto`. Auto mode usa un classifier de dos etapas + sandbox para decidir qué auto-aprobar; reduce el FPR de 8.5% a 0.4% comparado con la denegación liberal por defecto.

> Fuente: `/engineering/claude-code-auto-mode`

## 6. Instalar 3-5 servidores MCP que vayas a usar a diario

No más. Tool definitions cargadas upfront pueden consumir hasta 134K tokens en setups bloated. Empezar con:

- GitHub (issues / PRs / repos)
- Tu sistema de tickets (Linear, Jira)
- Una BD si trabajás con SQL a diario (Postgres MCP)

> Fuente: `/engineering/writing-tools-for-agents`, `/engineering/advanced-tool-use`

## 7. Verificar que las 6 skills se invocan

Después de copiar `.claude/skills/`, en una sesión de Claude Code escribir `/` y confirmar que aparecen:

- `/plan` — pensar antes de codear
- `/tdd` — test-first loop
- `/review` — revisar el diff con contexto fresco
- `/research` — investigar con subagentes en paralelo
- `/compact-resume` — escribir progreso + clear para continuar en otra sesión
- `/eval` — correr el harness de evals

Si no aparecen, revisar que el archivo es `.claude/skills/<nombre>/SKILL.md` y tiene frontmatter YAML con `name` y `description`.

> Fuente: `/engineering/equipping-agents-for-the-real-world-with-agent-skills`

## 8. Adoptar el ciclo explore → plan → code → commit

Para cualquier tarea no trivial:

1. Pedir a Claude que **lea archivos relevantes primero** (sin escribir código).
2. Invocar `/plan` para que produzca `PLAN.md`. Para presupuesto extra de razonamiento, decir "think hard" o "ultrathink" en el prompt.
3. Aprobar el plan (o pedir cambios).
4. Implementar.
5. Commit chico y descriptivo.

> Fuente: `/engineering/claude-code-best-practices`

## 9. Empezar siempre desde un git limpio

Si vas a correr Claude en modo autónomo o con `auto`, comiteá lo que tengas pending antes. Permite revertir cuando Claude tome una mala curva.

> Fuente: `/engineering/claude-code-best-practices`

## 10. Usar `/clear` entre tareas no relacionadas

Context rot es real: la recall del modelo se degrada con la longitud del contexto. Un `/clear` cuesta nada y resetea. Para sesiones largas en la misma tarea, `/compact` (sin argumentos — no acepta texto libre).

> Fuente: `/engineering/effective-context-engineering-for-ai-agents`

## 11. Para tareas que no caben en una sesión, usar `/compact-resume`

La skill escribe `claude-progress.txt` con tareas completadas, decisiones tomadas y próximos pasos. La siguiente sesión arranca leyendo ese archivo. Es el patrón que Anthropic usa para harnesses de larga duración (ej: build de un compilador en C con 16 agentes / 2000 sesiones).

> Fuente: `/engineering/effective-harnesses-for-long-running-agents`, `/engineering/building-c-compiler`

## 12. Para investigación con varias dimensiones, usar `/research`

Decompone la pregunta en 3-5 subpreguntas independientes y dispara subagentes en paralelo. Cada subagente recibe objetivo, formato de output, source guidance y boundaries. Este patrón le ganó al single-agent por 90.2% en el eval interno de Anthropic, pero usa ~15× más tokens que un chat — usalo para breadth, no para todo.

> Fuente: `/engineering/multi-agent-research-system`

## 13. Setup del eval harness mínimo

```bash
pip install anthropic
python evals/run.py
```

Empezar con las ~20 tasks de [`evals/tasks.jsonl`](evals/tasks.jsonl). Correr antes de cualquier cambio en prompts, tools o modelos. Comitear `evals/last_results.json` para detectar regresiones.

> Fuente: `/engineering/demystifying-evals-for-ai-agents`, `/engineering/multi-agent-research-system`

## 14. Para modo headless (CI / batch), usar `claude -p`

```bash
claude -p "Run the migration on all files in src/legacy/" --allowedTools "Read,Edit,Bash"
```

`--allowedTools` scopea las tools disponibles. Útil para fan-out de tareas mecánicas.

> Fuente: `/engineering/claude-code-best-practices`

## 15. Profundizar selectivamente

Cuando algo de lo de arriba te genere preguntas:

- **Por qué cada decisión**: [PRINCIPLES.md](PRINCIPLES.md)
- **Qué evitar y por qué**: [ANTIPATTERNS.md](ANTIPATTERNS.md)
- **Cómo encajan settings + hooks + skills + sandbox**: [docs/architecture.md](docs/architecture.md)
- **Patrones avanzados (multi-agent, RAG, think tool)**: [docs/patterns.md](docs/patterns.md)
- **Diseño de tools y MCP**: [docs/tools.md](docs/tools.md)
- **Source mapping completo**: [SOURCES.md](SOURCES.md)
