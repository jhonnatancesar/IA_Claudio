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

Testes em `tests/unit/test_execution.py` e `tests/unit/test_execution_id.py`.
