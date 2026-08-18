# Memória persistente

Documentação: docs/MEMORY.md. TASKs: TASK-044 a TASK-051.

Modelo de memória por usuário/aplicação, Memory Tool, busca estruturada, relevância/frequência/last used, retenção, limite fixo e auditoria de remoção.

- `memory_model.py` (TASK-044, TASK-045, TASK-047, TASK-048) — `Memory`
  (dataclass), `save_memory(owner_type, owner_id, content)`,
  `get_memory(memory_id)`. Persistência real no PostgreSQL local via
  `psycopg` (schema em `backend/app/db/migrations/0003_memory.sql` +
  `0004_memory_usage.sql`, tabela `memories`), mesmo padrão de
  `app.auth.users` (TASK-009). `list_memories_for_owner(owner_type,
  owner_id)` (TASK-045) garante separação de fato por dono.
  `search_memories(owner_type, owner_id, query)` (TASK-047) — busca por
  conteúdo (`ILIKE`). `record_memory_usage(memory_id)`/`relevance_score
  (memory, now)` (TASK-048) — rastreamento de uso (`use_count`,
  `last_used_at`) e pontuação heurística de relevância. Retenção
  (TASK-049), limite fixo (TASK-050) e auditoria de remoção (TASK-051)
  não são desta TASK.

Testes em `tests/integration/test_memory_model_integration.py` (persistência
real — sem teste unitário separado, mesmo padrão de `app.auth.users`) e
`tests/unit/test_memory_relevance.py` (`relevance_score`, função pura).
