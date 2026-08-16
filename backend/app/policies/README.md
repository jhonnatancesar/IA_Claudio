# Policy Engine

Documentação: docs/ORCHESTRATOR.md. TASKs: TASK-022.

Regras de execução por aplicação/contexto (ExecutionPolicy): permissões de pesquisa, limites, timeout, contexto.

- `execution_policy.py` (TASK-022) — `ExecutionPolicy` (dataclass imutável),
  `InvalidExecutionPolicyError`, `for_chat()`/`for_application(timeout_seconds=...)`.
  Só o modelo; quem aplica a política é o `ExecutionOrchestrator` (TASK-023).

Testes em `tests/unit/test_execution_policy.py`.
