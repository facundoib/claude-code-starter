# ANTIPATTERNS

Lista enumerada de prácticas que los 24 posts marcan explícitamente como problemáticas. Cada una con el por qué y la fuente. Si vas a hacer alguna de estas a propósito, conviene saber qué estás aceptando.

---

## Contexto y prompting

### A1. Prompts con casos exhaustivos en lugar de pocos canónicos
**Por qué**: el modelo generaliza mejor desde 3-5 ejemplos diversos canónicos que desde 30 ejemplos parecidos. Más ejemplos == más tokens consumidos sin lift de calidad.
**Fuente**: `/engineering/effective-context-engineering-for-ai-agents`

### A2. System prompts con if/else hardcoded
**Por qué**: el modelo trabaja mejor con principios al "right altitude" (suficientemente específicos para guiar, suficientemente flexibles para dejar margen heurístico). Cadenas de if/else son brittle: cualquier caso no contemplado falla y agregar uno más rompe el delicado equilibrio del prompt.
**Fuente**: `/engineering/effective-context-engineering-for-ai-agents`

### A3. No comprimir / no tomar notas en sesiones largas
**Por qué**: "context rot" es real — la recall del modelo se degrada al crecer el contexto. Acumular toda la historia conversacional sin compactar ni tomar notas estructuradas garantiza degradación.
**Fuente**: `/engineering/effective-context-engineering-for-ai-agents`

### A4. Cargar todas las tool definitions upfront cuando son muchas
**Por qué**: setups internos midieron 134K tokens consumidos en tool definitions antes de empezar la tarea. Eso es atención perdida. Usar Tool Search Tool con `defer_loading: true` o presentar las MCPs como código (Code Mode).
**Fuente**: `/engineering/advanced-tool-use`, `/engineering/code-execution-with-mcp`

---

## Tools y MCP

### A5. Wrappear cada endpoint API como tool separada
**Por qué**: Claude pierde contexto en cada hop entre tools. Consolidar tools alrededor de workflows (un `schedule_meeting`, no `list_users` + `list_events` + `create_event`).
**Fuente**: `/engineering/writing-tools-for-agents`

### A6. Devolver UUIDs cuando un nombre alcanza
**Por qué**: la retrieval del modelo es mejor sobre identificadores semánticos (slugs, names) que sobre UUIDs. Si tu API puede devolver `user.username`, devolvelo en vez de `user.id`.
**Fuente**: `/engineering/writing-tools-for-agents`

### A7. Tools que devuelven listas sin paginar / sin truncar
**Por qué**: una tool que devuelve 80K tokens contamina el contexto y desplaza información útil. Truncar a ~25K con mensaje útil ("usá filtros o paginación, hay 10K registros más"). Claude Code lo hace por default en sus tools internas.
**Fuente**: `/engineering/writing-tools-for-agents`

### A8. Errores opacos ("error 500", stack trace crudo)
**Por qué**: Claude no puede recuperarse de un error que no entiende. Mensajes accionables ("status='Pending' inválido — opciones: pending|shipped|delivered") permiten retry productivo.
**Fuente**: `/engineering/writing-tools-for-agents`

### A9. Tratar tool descriptions como throwaway
**Por qué**: las descriptions se cargan en cada turno. Editalas como editás prompts. La diferencia entre una description ambigua y una con ejemplos puede ser dígitos en un benchmark.
**Fuente**: `/engineering/writing-tools-for-agents`, `/engineering/swe-bench-sonnet`

---

## Permisos y sandbox

### A10. Auto-aprobar todos los permission prompts
**Por qué**: approval fatigue documentada — los usuarios aprueban el 93% de los prompts. La fricción del prompt no compra seguridad real, solo la ilusión de control. Mejor: sandbox + allowlist explícito + auto mode.
**Fuente**: `/engineering/claude-code-sandboxing`, `/engineering/claude-code-auto-mode`

### A11. Sandbox con un solo límite (solo filesystem o solo red)
**Por qué**: aislar solo filesystem permite exfiltración por `curl`. Aislar solo red permite leer `~/.ssh/id_rsa`. Hay que tener ambos.
**Fuente**: `/engineering/claude-code-sandboxing`

### A12. Permitir `Bash(curl *)` o `Bash(wget *)` en el allowlist
**Por qué**: vector de exfiltración estándar para sesiones con prompt-injection. Si necesitás fetchear, hacelo con una tool con whitelist de hosts, no con shell genérico.
**Fuente**: `/engineering/claude-code-sandboxing`

### A13. Permitir read/write a `~/.ssh`, `~/.aws`, `~/.gnupg`
**Por qué**: es el caso canónico de exfiltración de credenciales que Anthropic usa para argumentar por sandbox. Negar explícitamente, no asumir que el allowlist es suficiente.
**Fuente**: `/engineering/claude-code-sandboxing`

---

## Modo autónomo y sesiones

### A14. Correr en modo autónomo desde un git sucio
**Por qué**: si Claude toma una mala curva, no podés revertir. Commit early, commit often, partir de baseline limpio.
**Fuente**: `/engineering/claude-code-best-practices`

### A15. Aprobar sin leer en `--dangerously-skip-permissions`
**Por qué**: 8 vectores de ataque documentados (overeager behavior, honest mistakes, prompt injection, scope escalation, credential exploration, agent-inferred parameters, sharing via external services, safety-check bypass). Auto mode con classifier de dos etapas reduce el FPR de 8.5% a 0.4%; preferirlo.
**Fuente**: `/engineering/claude-code-auto-mode`

### A16. Inferir targets cuando el usuario no fue explícito
**Por qué**: "agent-inferred parameters" es uno de los attack vectors documentados — si el usuario dice "limpiá los logs", elegir qué carpeta limpiar es escalación de scope. Preguntar.
**Fuente**: `/engineering/claude-code-auto-mode`

### A17. Reintentar con flags que skipean verificaciones
**Por qué**: "safety-check bypass" — cuando un comando falla por una verificación, agregar `--force` o equivalente para saltearla es escalación. La verificación está ahí por algo.
**Fuente**: `/engineering/claude-code-auto-mode`

---

## Multi-agent y harnesses

### A18. Multi-agent para tareas que caben en una sesión
**Por qué**: 15× costo en tokens vs single-agent chat. Solo se justifica para breadth real con dimensiones independientes.
**Fuente**: `/engineering/multi-agent-research-system`

### A19. Multi-agent con estado mutable compartido entre subagentes
**Por qué**: el patrón documentado funciona porque cada subagente devuelve un finding inmutable y condensado. Si necesitás coordinación en tiempo real, single-agent gana.
**Fuente**: `/engineering/multi-agent-research-system`

### A20. Spawning 50 subagentes para una pregunta simple
**Por qué**: el effort tiene que escalar a la complejidad de la pregunta. Para fact-finding, 1 subagente con 3-10 calls. Para comparación, 2-4 con 10-15 calls cada uno. No más sin justificar.
**Fuente**: `/engineering/multi-agent-research-system`

### A21. Subagent briefs vagos ("research X")
**Por qué**: sin objetivo, formato de output, source guidance y boundaries explícitas, los subagentes producen resultados inconsistentes. La inversión en el brief se paga en la calidad del output.
**Fuente**: `/engineering/multi-agent-research-system`

### A22. Auto-evaluación del mismo agente que generó el output
**Por qué**: documentado en harness-design — single agents auto-evaluándose tienen confianza injustificada. Patrón correcto: generator + evaluator separados.
**Fuente**: `/engineering/harness-design-long-running-apps`

### A23. Compaction sola sin context resets en tareas largas
**Por qué**: hay un fenómeno de "context anxiety" donde el modelo arrastra referencias a turnos viejos. Para tareas multi-hora, mejor full reset con `claude-progress.txt` que compaction sola.
**Fuente**: `/engineering/harness-design-long-running-apps`, `/engineering/effective-harnesses-for-long-running-agents`

---

## Evals

### A24. Esperar a tener cientos de casos antes de empezar a evaluar
**Por qué**: 20-50 tareas extraídas de fallas reales superan a 500 casos hipotéticos. Empezar ahora.
**Fuente**: `/engineering/demystifying-evals-for-ai-agents`

### A25. Tests / evals one-sided (solo casos donde el behavior debe ocurrir)
**Por qué**: necesitás casos balanceados — cuándo SÍ debe ocurrir y cuándo NO. Sin la segunda mitad, no detectás false positives.
**Fuente**: `/engineering/demystifying-evals-for-ai-agents`

### A26. Single LLM-judge con múltiples rúbricas en una llamada
**Por qué**: una sola rúbrica con un solo score 0.0-1.0 matchea mejor con human raters que múltiples rúbricas en una call. Si tenés N rúbricas, hacé N llamadas.
**Fuente**: `/engineering/multi-agent-research-system`

### A27. Gradear el path en lugar del end-state
**Por qué**: los agentes son no-determinísticos; el mismo input produce caminos distintos válidos. Gradeá lo que produjo, no cómo.
**Fuente**: `/engineering/multi-agent-research-system`, `/engineering/demystifying-evals-for-ai-agents`

### A28. Reportar evals como point estimates sin varianza
**Por qué**: documentado en infrastructure-noise — los runs varían 5-6pp solo por ruido de infraestructura. Reportar media + std de N≥3 corridas, no un único score.
**Fuente**: `/engineering/infrastructure-noise`, `/engineering/multi-agent-research-system`

### A29. Soluciones de benchmark en plaintext en papers / blogs
**Por qué**: BrowseComp tuvo answers en HuggingFace dataset descriptions; Anthropic detectó 11 problemas contaminados en 1 corrida. Si publicás un eval, las respuestas no van en plaintext.
**Fuente**: `/engineering/eval-awareness-browsecomp`

---

## Tools de archivo y diff

### A30. File-edit tools sin match exacto requerido
**Por qué**: el setup que llegó a 49% en SWE-bench Verified usaba `old_str`/`new_str` con **un solo match exacto requerido** — match ambiguo == error explícito. Sin esa restricción, Claude edita el archivo equivocado más seguido.
**Fuente**: `/engineering/swe-bench-sonnet`

### A31. Output bloated en tests / runs
**Por qué**: imprimir miles de bytes de salida útil en cada run contamina el contexto del agente. "Put yourself in Claude's shoes" — si vos no podés leer 60kb de stdout, Claude tampoco.
**Fuente**: `/engineering/building-c-compiler`

---

## Desktop Extensions y MCP

### A32. Distribuir extensions que requieren editar JSON manualmente
**Por qué**: los `user_config` declarados en el manifest son la forma. Si tu usuario tiene que abrir `claude_desktop_config.json` con un editor de texto, perdés.
**Fuente**: `/engineering/desktop-extensions`

### A33. Secrets en config plaintext
**Por qué**: el flag `sensitive: true` en el manifest los manda al OS keychain. Plaintext en archivo de config es leak por defecto.
**Fuente**: `/engineering/desktop-extensions`

---

## Releases y cambios

### A34. Cambios al system prompt sin eval suite
**Por qué**: el incidente de abril 2026 — un cambio de "verbosity instruction" degradó 3pp los evals de Opus 4.6/4.7. Sin evals continuas, regresiones de comportamiento son invisibles.
**Fuente**: `/engineering/april-23-postmortem`

### A35. Cache optimization sin verificación de que el thinking se preserva
**Por qué**: un bug que limpiaba el thinking en cada turn (debió ser una sola vez) degradó silenciosamente la calidad por semanas. Las optimizaciones de cache requieren tests de no-regresión específicos.
**Fuente**: `/engineering/april-23-postmortem`

---

## Misc

### A36. Asumir que tests passing == job done
**Por qué**: en el build del compilador de C, los tests pasaban antes que el compilador funcionara end-to-end. Tests son condición necesaria, no suficiente. Verificación adicional (deployable, smoke test, end-to-end) requerida.
**Fuente**: `/engineering/building-c-compiler`

### A37. Encodear assumptions sobre capacidades del modelo en el harness
**Por qué**: cada release de modelo nuevo es ocasión de revisar qué piezas del harness ya no son necesarias. La complejidad del harness no debe persistir más allá de su utilidad.
**Fuente**: `/engineering/harness-design-long-running-apps`, `/engineering/managed-agents`
