# Orquestrador

Documentação: docs/ARCHITECTURE.md e docs/ORCHESTRATOR.md. TASKs: TASK-020 a TASK-030.

Núcleo determinístico: Execution, ExecutionPolicy, ExecutionOrchestrator, planejamento, validação de plano, execução por etapas, replanejamento, max_steps, detecção de loop, cancelamento.

- `execution.py` (TASK-020) — `Execution` (dataclass), `ExecutionStatus`
  (`PENDING`/`RUNNING`/`COMPLETED`/`FAILED`), `InvalidExecutionStateError`.
  Modelo de dados e transições de estado (`start()`/`add_step()`/
  `complete()`/`fail()`); nada de política, execução real, `max_steps` ou
  detecção de loop — isso vem nas próximas TASKs deste bloco.

Testes em `tests/unit/test_execution.py`.
