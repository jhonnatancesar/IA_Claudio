# Fontes e reputação

Documentação: docs/TRUST_GUARDRAILS.md. TASKs: TASK-059 a TASK-066.

Cadastro de fontes (PRIMARY/SECONDARY/UNKNOWN), reputação (LOW/MEDIUM/HIGH), histórico de reputação, blacklist, bloqueio automático e desbloqueio (somente ADMIN).

- `source_registry.py` (TASK-059, TASK-060) — `Source` (dataclass),
  `register_source(identifier, source_type=UNKNOWN)` (idempotente por
  `identifier`), `get_source(source_id)`,
  `get_source_by_identifier(identifier)`. Persistência real no
  PostgreSQL local (`backend/app/db/migrations/0010_sources.sql` +
  `0011_source_type.sql`). `SourceType`
  (`PRIMARY`/`SECONDARY`/`UNKNOWN`)/`set_source_type(source_id,
  source_type)` (TASK-060) — reclassifica uma fonte já registrada.
  Reputação (TASK-061+) e blacklist (TASK-064+) não são desta TASK.

Testes em `tests/integration/test_source_registry_integration.py`
(persistência/idempotência/tipo reais) e `tests/unit/test_source_registry.py`
(validação de `identifier` vazio, enum de tipo).
