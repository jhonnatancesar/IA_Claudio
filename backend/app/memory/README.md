# Memória persistente

Documentação: docs/MEMORY.md. TASKs: TASK-044 a TASK-051.

Modelo de memória por usuário/aplicação, Memory Tool, busca estruturada, relevância/frequência/last used, retenção, limite fixo e auditoria de remoção.

- `memory_model.py` (TASK-044, TASK-045, TASK-047, TASK-048, TASK-049,
  TASK-051) — `Memory` (dataclass), `save_memory(owner_type, owner_id,
  content)`, `get_memory(memory_id)`. Persistência real no PostgreSQL
  local via `psycopg` (schema em `backend/app/db/migrations/0003_memory.sql`
  + `0004_memory_usage.sql` + `0005_memory_removal_audit.sql`, tabelas
  `memories`/`memory_removal_audit`), mesmo padrão de `app.auth.users`
  (TASK-009). `list_memories_for_owner(owner_type, owner_id)` (TASK-045)
  garante separação de fato por dono. `search_memories(owner_type,
  owner_id, query)` (TASK-047) — busca por conteúdo (`ILIKE`).
  `record_memory_usage(memory_id)`/`relevance_score(memory, now)`
  (TASK-048) — rastreamento de uso e pontuação heurística de relevância.
  `delete_memory(memory_id, reason)` (TASK-049, TASK-051) — remove e
  grava auditoria mínima (`memory_id`/`owner_type`/`owner_id`/`reason`/
  `removed_at`, sem `content`) na mesma transação.
  `list_removal_audit_for_owner(owner_type, owner_id)` (TASK-051) lê o
  histórico de remoções.
- `retention_policy.py` (TASK-049, TASK-050, TASK-051) —
  `is_eligible_for_retention_removal(memory, now, ...)` e
  `apply_retention_policy(owner_type, owner_id, now, ...)`: remove
  memórias antigas (`created_at`) e de baixa relevância/pouco uso
  (`relevance_score`, TASK-048), com `reason=REMOVAL_REASON_RETENTION`.
  `MAX_MEMORIES_PER_OWNER = 500`/`enforce_memory_limit(owner_type,
  owner_id, now, ...)` (TASK-050): limite fixo por dono, remove as menos
  relevantes primeiro quando excedido, com
  `reason=REMOVAL_REASON_MEMORY_LIMIT`.

Com esta TASK, o bloco "Memória" (TASK-044 a TASK-051) está completo.

Testes em `tests/integration/test_memory_model_integration.py` e
`tests/integration/test_retention_policy_integration.py` (persistência/
remoção real) e `tests/unit/test_memory_relevance.py`/
`tests/unit/test_retention_policy.py`/`tests/unit/test_memory_removal_audit.py`
(funções puras/validação).
