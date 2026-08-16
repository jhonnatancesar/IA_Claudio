# Orquestrador

Documentação: docs/ARCHITECTURE.md e docs/ORCHESTRATOR.md. TASKs: TASK-020 a TASK-030.

Núcleo determinístico: Execution, ExecutionPolicy, ExecutionOrchestrator, planejamento, validação de plano, execução por etapas, replanejamento, max_steps, detecção de loop, cancelamento.

- `execution.py` (TASK-020) — `Execution` (dataclass), `ExecutionStatus`
  (`PENDING`/`RUNNING`/`COMPLETED`/`FAILED`), `InvalidExecutionStateError`,
  `Execution.new(origin)` (fábrica com `execution_id` gerado — TASK-021).
  Modelo de dados e transições de estado (`start()`/`add_step()`/
  `complete()`/`fail()`/`set_last_observation()` — TASK-026); nada de
  política, `max_steps` ou detecção de loop — isso vem nas próximas TASKs.
- `execution_id.py` (TASK-021) — `generate_execution_id()` (UUID4). Reenvios/
  retries sempre geram um novo, nunca reaproveitam.
- `orchestrator.py` (TASK-023) — `ExecutionOrchestrator(provider, policy,
  tool_executor=None)`. `run_step(execution, objective, model)` faz um passo
  real: compõe prompt (com histórico + observações), chama o provider,
  valida a resposta, valida o plano, registra a etapa, conclui se `RESPOND`.
  `run_until_response(execution, objective, model)` (TASK-026) chama
  `run_step` em loop, executando `USE_TOOL` via `tool_executor` e
  realimentando o resultado, até `RESPOND`. `max_steps` ainda não aplicado
  (TASK-028) — sem isso, pode entrar em laço sem fim.
- `planner.py` (TASK-024) — `plan_initial_step(orchestrator, execution,
  objective, model)`/`ExecutionAlreadyPlannedError`. Casca fina sobre
  `run_step`, só para a primeira etapa de uma execução nova.
- `plan_validator.py` (TASK-025) — `validate_plan(step, execution, policy)`.
  Checa `execution_id` da etapa contra a execução e `WEB_SEARCH` contra
  `ExecutionPolicy.web_search_allowed`; chamado dentro de `run_step`.

Testes em `tests/unit/test_execution.py`, `tests/unit/test_execution_id.py`,
`tests/unit/test_execution_observation.py`,
`tests/unit/test_execution_orchestrator.py`,
`tests/unit/test_execution_orchestrator_tool_loop.py`,
`tests/unit/test_planner.py`, `tests/unit/test_plan_validator.py` (provider e
tool_executor fakes) e
`tests/integration/test_execution_orchestrator_integration.py`,
`tests/integration/test_planner_integration.py` (Ollama real; pulam
automaticamente se indisponível).
