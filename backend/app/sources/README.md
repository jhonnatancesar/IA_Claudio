# Fontes e reputação

Documentação: docs/TRUST_GUARDRAILS.md. TASKs: TASK-059 a TASK-066.

Cadastro de fontes (PRIMARY/SECONDARY/UNKNOWN), reputação (LOW/MEDIUM/HIGH), histórico de reputação, blacklist, bloqueio automático e desbloqueio (somente ADMIN).

- `source_registry.py` (TASK-059, TASK-060, TASK-061, TASK-063,
  TASK-064) — `Source` (dataclass), `register_source(identifier,
  source_type=UNKNOWN, reputation=MEDIUM)` (idempotente por
  `identifier`), `get_source(source_id)`,
  `get_source_by_identifier(identifier)`. Persistência real no
  PostgreSQL local (`backend/app/db/migrations/0010_sources.sql` +
  `0011_source_type.sql` + `0012_source_reputation.sql` +
  `0013_source_reputation_history.sql` + `0014_source_blacklist.sql`).
  `SourceType` (`PRIMARY`/`SECONDARY`/`UNKNOWN`)/`set_source_type
  (source_id, source_type)` (TASK-060). `SourceReputation`
  (`LOW`/`MEDIUM`/`HIGH`)/`set_source_reputation(source_id, reputation)`
  (TASK-061) — grava histórico (`ReputationHistoryEntry`/
  `list_reputation_history`, TASK-063) só quando o valor muda.
  `block_source`/`unblock_source(source_id, origin, reason,
  responsible=None)` (TASK-064) — mecânicos, gravam
  `BlacklistEntry`/`list_blacklist_entries` a cada chamada;
  `SourceBlacklistStateError` para bloquear já bloqueada/desbloquear não
  bloqueada. Nenhum dos dois checa quem está autorizado a chamar.
- `reputation_rule.py` (TASK-062) — `update_reputation(current,
  was_accurate)` (função pura: um degrau por vez,
  `HIGH↔MEDIUM↔LOW`) e `update_source_reputation(source_id,
  was_accurate)` — busca a fonte, calcula a nova reputação e só grava se
  mudar (histórico segue automaticamente via `set_source_reputation`).
- `auto_block_rule.py` (TASK-065) — `is_eligible_for_auto_block
  (reputation)` (função pura: hoje só `reputation == LOW`) e
  `auto_block_after_validation(source_id, was_accurate)` — encadeia
  `update_source_reputation` com `block_source` (`origin=AGENT`) quando
  a reputação cai para `LOW`, sem bloquear de novo uma fonte já
  bloqueada. Alerta no painel (seção 14/15) não é desta TASK — painel
  ainda não existe.
- `unblock_rule.py` (TASK-066) — `admin_unblock_source(source_id, role,
  responsible, reason)`: só desbloqueia se `role` for `ADMIN`
  (`app.auth.roles.require_admin`, TASK-010, reaproveitado — mesmo
  código de erro `FORBIDDEN_ADMIN_ONLY`), sem exceção mesmo quando foi o
  agente que bloqueou. Com esta TASK, o bloco "Fontes" (TASK-059 a
  TASK-066) está completo.

Testes em `tests/integration/test_source_registry_integration.py`,
`tests/integration/test_reputation_rule_integration.py`,
`tests/integration/test_source_blacklist_integration.py`,
`tests/integration/test_auto_block_rule_integration.py`,
`tests/integration/test_unblock_rule_integration.py`
(persistência/idempotência/tipo/reputação/atualização/histórico/blacklist/bloqueio
automático/desbloqueio ADMIN reais) e `tests/unit/test_source_registry.py`/
`tests/unit/test_reputation_rule.py`/`tests/unit/test_source_blacklist.py`/
`tests/unit/test_auto_block_rule.py`/`tests/unit/test_unblock_rule.py`
(validação de campos vazios, enums, regras puras).
