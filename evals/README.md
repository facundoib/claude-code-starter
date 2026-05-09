# Eval harness

Suite mínima para detectar regresiones cuando cambiás CLAUDE.md, skills, prompts, modelos o tools. Empieza con 20 tareas — extendé desde ahí.

## Setup

```bash
pip install -r evals/requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

## Correr

```bash
python evals/run.py
```

Cada task corre **3 veces** (configurable en `run.py::TRIALS_PER_TASK`). Los resultados se escriben a `evals/results/<timestamp>.json`. La consola imprime pass rate, tokens, wall time, y diff contra `evals/last_results.json` si existe.

## Setear baseline por primera vez

`evals/last_results.json` no viene en el repo — la primera corrida lo bootstrappea. Después de la primera corrida exitosa:

```bash
cp evals/results/<latest>.json evals/last_results.json
git add evals/last_results.json && git commit -m "Set eval baseline"
```

A partir de ahí, cada corrida se compara contra ese baseline. Para refrescarlo después de un cambio que mejora el pass rate sin regresiones, repetí los dos comandos.

## Cuándo correr

- **Antes** de cada cambio en `CLAUDE.md`.
- **Antes** de modificar `.claude/skills/*`.
- **Antes** de cambiar modelo (`claude-sonnet-4-6` ↔ `claude-opus-4-7` etc).
- **Antes** de agregar/sacar tools o servidores MCP.
- **Después** de cada cambio: confirmar que no hay regresiones antes de commit.

> Fuente: `/engineering/demystifying-evals-for-ai-agents` — empezar con 20-50 tareas extraídas de fallas reales y correrlas en cada release.

## Cómo se interpreta el output

```
============================================================
Model:           claude-sonnet-4-6
Tasks:           20
Trials per task: 3
Pass rate:       86.7%
Tokens in/out:   12450 / 3210
Wall time:       54.3s
Saved to:        evals/results/20260508T123000Z.json
============================================================

Tasks with at least one failed trial:
  t06 (67%): Reasoning trap (siblings)
  t11 (33%): Refusal of PII overreach
```

- **Pass rate** = promedio sobre las 60 corridas (20 tasks × 3 trials).
- **Tasks con failures** = tasks donde al menos 1 de los 3 trials falló. Investigá esos antes de declarar success.

Cuando hay diff vs baseline:

```
REGRESSIONS (1) — DO NOT update baseline:
  t06: 100% → 67%
```

Si aparece "REGRESSIONS", **no sobrescribas el baseline**. Investigá. Probablemente el cambio que hiciste rompió algo.

> Fuente: `/engineering/april-23-postmortem` — el incidente concreto donde un cambio "menor" al system prompt degradó 3pp evals de Opus.

## Anatomía de una task

`evals/tasks.jsonl`, una task por línea:

```json
{
  "id": "t01",
  "summary": "Brief description for logs",
  "system": "Optional system prompt for this specific task",
  "prompt": "The user message to send to the model",
  "verifier": "exact_match | regex_match | contains_all | contains_none | llm_judge",
  "args": { "expected": "...", "pattern": "...", "needles": ["...", "..."], "rubric": "..." }
}
```

### Tipos de verifier

| Verifier | Args | Cuándo usarlo |
|----------|------|---------------|
| `exact_match` | `expected: "..."` | Output exacto requerido (case-insensitive). Para single-word/single-number replies. |
| `regex_match` | `pattern: "..."` | Output debe matchear regex (multiline). Para format constraints. |
| `contains_all` | `needles: ["...", "..."]` | Output debe contener todos los strings (case-insensitive). Para cobertura semántica. |
| `contains_none` | `needles: ["...", "..."]` | Output NO debe contener ninguno. Para refusals y safety checks. |
| `llm_judge` | `rubric: "..."` | Cuando ningún check determinístico aplica. Usa `judge.py` con score 0.0-1.0. |

### Por qué N≥3 trials por task

Los modelos son no-determinísticos. La misma prompt produce paths distintos, a veces con outcomes distintos. Reportar pass rate sobre múltiples trials da signal honesto; un único trial es coin flip.

> Fuente: `/engineering/infrastructure-noise` — Anthropic midió 6pp de variance entre setups con configs distintas en la misma eval. Sin variance check, regresiones de noise se confunden con regresiones reales.

## Cómo agregar tasks

Tres reglas:

1. **Las tasks vienen de fallas reales**, no de casos hipotéticos. Cada vez que Claude falla algo concreto en tu workflow real, agregá una task que captura ese caso.

2. **Balanced sets**: si testeás "Claude debe rechazar X", también testeá "Claude debe NO rechazar Y" (caso similar pero legítimo). Sin ambos lados, optimizás solo para uno.

3. **Verifier antes que rubric vago**: preferí `contains_none: ["DROP TABLE", "UNION SELECT"]` sobre `llm_judge: "el output no debe ser malicioso"`. Lo determinístico es repetible.

> Fuente: `/engineering/demystifying-evals-for-ai-agents`

## LLM-as-judge (`judge.py`)

Para casos donde no hay forma determinística de verificar (calidad de explicación, tono apropiado, etc.):

```python
from evals.judge import judge

result = judge(
    rubric="The response should explain prompt caching accurately, in under 100 words.",
    response=model_output_text,
)
# → {"score": 0.85, "reasoning": "Accurate, but slightly verbose."}
```

Una sola rúbrica por call, un solo score 0.0-1.0. Si querés evaluar accuracy + tone + length, son tres calls separadas, no una con tres rúbricas.

> Fuente: `/engineering/multi-agent-research-system`

## Cost estimate

20 tasks × 3 trials × ~500 tokens promedio = ~30K tokens por corrida. Con `claude-sonnet-4-6` (default): ~$0.10 USD por corrida. Con `claude-haiku-4-5-20251001` (judge): ~$0.02 USD.

Para suites más grandes (200 tasks × 5 trials), considerá:
- Bajar a `claude-haiku-4-5-20251001` para tasks que no requieren reasoning profundo.
- Cachear el system prompt si todas las tasks lo comparten (`prompt_caching` reduce repeated input tokens).

> Fuente: `/engineering/contextual-retrieval` — el truco de prompt caching para amortizar costos repetidos.
