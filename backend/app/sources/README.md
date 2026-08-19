# Fontes e reputação

Documentação: docs/TRUST_GUARDRAILS.md. TASKs: TASK-059 a TASK-066.

Cadastro de fontes (PRIMARY/SECONDARY/UNKNOWN), reputação (LOW/MEDIUM/HIGH), histórico de reputação, blacklist, bloqueio automático e desbloqueio (somente ADMIN).

- `source_registry.py` (TASK-059, TASK-060, TASK-061) — `Source`
  (dataclass), `register_source(identifier, source_type=UNKNOWN,
  reputation=MEDIUM)` (idempotente por `identifier`),
  `get_source(source_id)`, `get_source_by_identifier(identifier)`.
  Persistência real no PostgreSQL local
  (`backend/app/db/migrations/0010_sources.sql` +
  `0011_source_type.sql` + `0012_source_reputation.sql`). `SourceType`
  (`PRIMARY`/`SECONDARY`/`UNKNOWN`)/`set_source_type(source_id,
  source_type)` (TASK-060) — reclassifica uma fonte já registrada.
  `SourceReputation` (`LOW`/`MEDIUM`/`HIGH`)/`set_source_reputation
  (source_id, reputation)` (TASK-061) — troca mecânica de reputação, sem
  a regra de quando trocar.
- `reputation_rule.py` (TASK-062) — `update_reputation(current,
  was_accurate)` (função pura: um degrau por vez,
  `HIGH↔MEDIUM↔LOW`) e `update_source_reputation(source_id,
  was_accurate)` — busca a fonte, calcula a nova reputação e só grava se
  mudar. Histórico de mudanças (TASK-063) e blacklist (TASK-064+) não
  são desta TASK.

Testes em `tests/integration/test_source_registry_integration.py`,
`tests/integration/test_reputation_rule_integration.py`
(persistência/idempotência/tipo/reputação/atualização reais) e
`tests/unit/test_source_registry.py`/`tests/unit/test_reputation_rule.py`
(validação de `identifier` vazio, enums, regra pura).
