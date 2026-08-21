# Orquestrador

Documentação: docs/ARCHITECTURE.md e docs/ORCHESTRATOR.md. TASKs: TASK-020 a TASK-030, TASK-079.

Núcleo determinístico: Execution, ExecutionPolicy, ExecutionOrchestrator, planejamento, validação de plano, execução por etapas, replanejamento, max_steps, detecção de loop, cancelamento.

- `execution.py` (TASK-020) — `Execution` (dataclass), `ExecutionStatus`
  (`PENDING`/`RUNNING`/`COMPLETED`/`FAILED`/`CANCELLED` — TASK-030),
  `InvalidExecutionStateError`, `Execution.new(origin)` (fábrica com
  `execution_id` gerado — TASK-021). Modelo de dados e transições de estado
  (`start()`/`add_step()`/`complete()`/`fail()`/`cancel()`/
  `set_last_observation()`); nada de política — isso é o
  `ExecutionOrchestrator`.
- `execution_id.py` (TASK-021) — `generate_execution_id()` (UUID4). Reenvios/
  retries sempre geram um novo, nunca reaproveitam.
- `cancellation.py` (TASK-030) — `CancellationToken`
  (`cancel(reason)`/`is_cancelled`), `ExecutionCancelledError`. Sinalizador
  cooperativo, sem threads/async.
- `orchestrator.py` (TASK-023, TASK-079) — `ExecutionOrchestrator(provider,
  policy, tool_executor=None, loop_repeat_threshold=3)`. `run_step(execution,
  objective, model, cancellation_token=None, trace=None)` faz um passo real:
  cancela se o token já estiver cancelado (TASK-030, antes de qualquer outra
  checagem), checa `max_steps` (TASK-028, código 4004), compõe prompt (com
  histórico + observações), cronometra e chama o provider, valida a
  resposta, valida o plano, registra a etapa (em `execution` e, se `trace`
  for dado, em `trace.add_step` com o tempo da chamada — TASK-079), conclui
  se `RESPOND` ou checa detecção de loop (TASK-029, código 4005) caso
  contrário. `run_until_response(execution, objective, model,
  cancellation_token=None, trace=None)` (TASK-026) chama `run_step` em
  loop, executando `USE_TOOL` via `tool_executor` (cronometrado e registrado
  em `trace.record_tool_execution` se `trace` for dado) e realimentando o
  resultado, até `RESPOND`, `max_steps`, um loop detectado ou cancelamento.
  `trace: ExecutionTrace | None` (`app.observability.execution_trace`) é
  `None` por padrão — nada muda para quem chama sem ele.
- `loop_detector.py` (TASK-029) — `detect_loop(execution, threshold=3)`.
  Loop = últimas `threshold` etapas com `action`/`tool`/`parameters`
  idênticos; parâmetros diferentes não contam (progresso real).
- `planner.py` (TASK-024, TASK-079) — `plan_initial_step(orchestrator,
  execution, objective, model, cancellation_token=None,
  trace=None)`/`ExecutionAlreadyPlannedError`. Casca fina sobre `run_step`,
  só para a primeira etapa de uma execução nova; repassa `trace` como
  repassa `cancellation_token`.
- `plan_validator.py` (TASK-025) — `validate_plan(step, execution, policy)`.
  Checa `execution_id` da etapa contra a execução e `WEB_SEARCH` contra
  `ExecutionPolicy.web_search_allowed`; chamado dentro de `run_step`.
- `replanner.py` (TASK-027, TASK-079) — `replan(orchestrator, old_execution,
  objective, model, cancellation_token=None,
  trace=None)`/`CannotReplanFinishedExecutionError`. Encerra `old_execution`
  (`fail()`) e cria uma execução nova com `plan_initial_step` — mesmas
  regras do plano inicial, incluindo `validate_plan`; repassa `trace`.
  Rejeita `old_execution` em qualquer estado terminal, incluindo
  `CANCELLED`.

Testes em `tests/unit/test_execution.py`, `tests/unit/test_execution_id.py`,
`tests/unit/test_execution_observation.py`,
`tests/unit/test_execution_orchestrator.py`,
`tests/unit/test_execution_orchestrator_tool_loop.py`,
`tests/unit/test_planner.py`, `tests/unit/test_plan_validator.py`,
`tests/unit/test_replanner.py`, `tests/unit/test_max_steps.py`,
`tests/unit/test_loop_detector.py`,
`tests/unit/test_orchestrator_loop_detection.py`,
`tests/unit/test_cancellation.py`,
`tests/unit/test_orchestrator_cancellation.py`,
`tests/unit/test_orchestrator_trace.py` (registro de etapas/tempos no
Execution Trace) (provider e tool_executor fakes) e
`tests/integration/test_execution_orchestrator_integration.py`,
`tests/integration/test_planner_integration.py` (Ollama real; pulam
automaticamente se indisponível).
