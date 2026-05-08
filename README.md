# claude-code-starter

Setup opinado para que un dev arranque a usar Claude Code productivamente en menos de 30 minutos. Todas las recomendaciones acá vienen exclusivamente de los 24 posts publicados en [anthropic.com/engineering](https://www.anthropic.com/engineering) — sin opiniones de terceros, sin "best practices" inventadas, sin recetas de Twitter. Cada decisión cita el post fuente.

## Qué es

- Un **template** clonable (o copiable archivo por archivo) con `CLAUDE.md`, `.claude/settings.json`, 6 skills custom y un eval harness mínimo, todo verificado contra la documentación oficial actual de Claude Code.
- Una **guía corta** (`QUICKSTART.md`) que te lleva del cero al setup productivo en pasos numerados.
- Una **referencia razonada** (`PRINCIPLES.md`, `ANTIPATTERNS.md`, `docs/`) para cuando necesites entender el por qué detrás de cada elección.
- Una **tabla de procedencia** (`SOURCES.md`) que mapea cada recomendación al post de Anthropic del que sale.

## Qué NO es

- No es una opinión sobre cómo usar Claude. Si Anthropic no lo dijo en uno de esos 24 posts, no está acá.
- No es exhaustivo. Curaduría agresiva: lo que el 80/20 indica que mueve la aguja, no toda recomendación posible.
- No es estable como API. Anthropic actualiza el blog seguido (varios posts citados tienen update notes). Cuando algo cambia, este repo se ajusta — o queda flaggeado en `SOURCES.md`.
- No incluye claims de marketing del tipo "10× tu productividad". Si hay un número acá, viene con cita inline al post que lo midió.

## Cómo usar

### Opción A — clonar como base

```bash
git clone https://github.com/facundoib/claude-code-starter.git mi-proyecto
cd mi-proyecto
rm -rf .git && git init
```

Editar `templates/CLAUDE.md` con info de tu proyecto, copiarlo a la raíz como `CLAUDE.md`, y customizar `.claude/settings.json` para tus paths.

### Opción B — copiar archivos a un proyecto existente

```bash
# Desde la raíz de tu proyecto:
cp -r path/al/claude-code-starter/.claude .
cp path/al/claude-code-starter/templates/CLAUDE.md ./CLAUDE.md
```

Editar ambos para tu stack.

En cualquiera de las dos, el siguiente paso es leer [QUICKSTART.md](QUICKSTART.md).

## Estructura

```
claude-code-starter/
├── README.md              ← este archivo
├── QUICKSTART.md          ← día-1 paso a paso
├── PRINCIPLES.md          ← por qué cada decisión
├── ANTIPATTERNS.md        ← qué NO hacer
├── SOURCES.md             ← tabla 24 posts → secciones
├── templates/
│   ├── CLAUDE.md          ← template anotado para copiar a tu repo
│   └── settings.json      ← settings.json verificado contra docs actuales
├── .claude/
│   ├── settings.json      ← config real de este repo (mismo formato)
│   └── skills/
│       ├── plan/SKILL.md
│       ├── tdd/SKILL.md
│       ├── review/SKILL.md
│       ├── research/SKILL.md
│       ├── compact-resume/SKILL.md
│       └── eval/SKILL.md
├── docs/
│   ├── architecture.md    ← cómo encajan settings/hooks/skills/sandbox
│   ├── patterns.md        ← long-running, multi-agent, RAG, think tool
│   └── tools.md           ← tool design + MCP setup
└── evals/
    ├── tasks.jsonl
    ├── run.py
    ├── judge.py
    └── README.md
```

## Procedencia

Las 24 fuentes están listadas en [SOURCES.md](SOURCES.md) con la sección de este repo que cada una alimenta. Los claims dudosos del research inicial fueron verificados contra:

- `code.claude.com/docs` para la sintaxis de `settings.json`, hooks, skills, slash commands y permission modes.
- Los posts mismos para los claims numéricos (porcentajes, costos, tiempos).

Cuando un claim no se pudo verificar contra docs públicas, se omitió. Esto pasó con `.mcpb` ("formerly `.dxt`") — la referencia salió del repo.

## Compatibilidad

Verificado contra:
- Claude Code 2.0+ (sandbox via `/sandbox`, skills en `.claude/skills/`, hooks con estructura anidada).
- API: Sonnet 4.6 / Opus 4.7 / Haiku 4.5.

Si tu Claude Code es anterior a 2.0, el path de skills antes era `.claude/commands/`. Ese formato sigue funcionando pero no es el recomendado.

## Cómo contribuir

Si encontrás:
- Un claim mal citado o que no aparece en el post fuente,
- Un comando o setting que cambió en docs y este repo no refleja,
- Un post nuevo de Anthropic engineering que justifica un cambio,

abrí un issue con link al post y la línea que lo respalda. PRs sin cita al post se cierran.

## Licencia

MIT. Ver [LICENSE](LICENSE).
