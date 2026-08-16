# Orquestrador

Documentação: docs/ARCHITECTURE.md e docs/ORCHESTRATOR.md. TASKs: TASK-020 a TASK-030.

Núcleo determinístico: Execution, ExecutionPolicy, ExecutionOrchestrator, planejamento, validação de plano, execução por etapas, replanejamento, max_steps, detecção de loop, cancelamento.

- `execution.py` (TASK-020) — `Execution` (dataclass), `ExecutionStatus`
  (`PENDING`/`RUNNING`/`COMPLETED`/`FAILED`), `InvalidExecutionStateError`,
  `Execution.new(origin)` (fábrica com `execution_id` gerado — TASK-021).
  Modelo de dados e transições de estado (`start()`/`add_step()`/
  `complete()`/`fail()`); nada de política, execução real, `max_steps` ou
  detecção de loop — isso vem nas próximas TASKs deste bloco.
- `execution_id.py` (TASK-021) — `generate_execution_id()` (UUID4). Reenvios/
  retries sempre geram um novo, nunca reaproveitam.
- `orchestrator.py` (TASK-023) — `ExecutionOrchestrator(provider, policy)`.
  `run_step(execution, objective, model)` faz um passo real: compõe prompt,
  chama o provider, valida a resposta, registra a etapa, conclui se
  `RESPOND`. Política ainda não aplicada (guardada só para TASKs futuras).
- `planner.py` (TASK-024) — `plan_initial_step(orchestrator, execution,
  objective, model)`/`ExecutionAlreadyPlannedError`. Casca fina sobre
  `run_step`, só para a primeira etapa de uma execução nova.
- `plan_validator.py` (TASK-025) — `validate_plan(step, execution, policy)`.
  Checa `execution_id` da etapa contra a execução e `WEB_SEARCH` contra
  `ExecutionPolicy.web_search_allowed`; chamado dentro de `run_step`.

Testes em `tests/unit/test_execution.py`, `tests/unit/test_execution_id.py`,
`tests/unit/test_execution_orchestrator.py`, `tests/unit/test_planner.py`,
`tests/unit/test_plan_validator.py` (provider fake) e
`tests/integration/test_execution_orchestrator_integration.py`,
`tests/integration/test_planner_integration.py` (Ollama real; pulam
automaticamente se indisponível).
