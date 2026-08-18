# Memória persistente

Documentação: docs/MEMORY.md. TASKs: TASK-044 a TASK-051.

Modelo de memória por usuário/aplicação, Memory Tool, busca estruturada, relevância/frequência/last used, retenção, limite fixo e auditoria de remoção.

- `memory_model.py` (TASK-044, TASK-045, TASK-047) — `Memory` (dataclass),
  `save_memory(owner_type, owner_id, content)`, `get_memory(memory_id)`.
  Persistência real no PostgreSQL local via `psycopg` (schema em
  `backend/app/db/migrations/0003_memory.sql`, tabela `memories`), mesmo
  padrão de `app.auth.users` (TASK-009). `list_memories_for_owner
  (owner_type, owner_id)` (TASK-045) garante separação de fato por dono —
  nunca mistura memórias de outro dono. `search_memories(owner_type,
  owner_id, query)` (TASK-047) — busca por conteúdo (`ILIKE`), sem ranking
  por relevância (TASK-048). Relevância/frequência/last_used (TASK-048),
  retenção (TASK-049), limite fixo (TASK-050) e auditoria de remoção
  (TASK-051) não são desta TASK.

Testes em `tests/integration/test_memory_model_integration.py` (persistência
real — sem teste unitário separado, mesmo padrão de `app.auth.users`).
