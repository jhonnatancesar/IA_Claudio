# TASK-064 — Criar blacklist

Status: **Concluída em 2026-08-19**

## Objetivo

Criar blacklist, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Fontes") e `docs/TRUST_GUARDRAILS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fontes" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TRUST_GUARDRAILS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-063 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TRUST_GUARDRAILS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de fontes/reputação/blacklist para este comportamento específico, conforme docs/TESTING.md.

## Documentação afetada

`docs/TRUST_GUARDRAILS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. Criado schema
`backend/app/db/migrations/0014_source_blacklist.sql` (coluna
`is_blocked` em `sources`; tabela `source_blacklist_entries`:
`source_id` com `ON DELETE CASCADE`, `action`
(`BLOCK`/`UNBLOCK`), `origin` (`AGENT`/`ADMIN`), `responsible`, `reason`,
`created_at`), aplicado no PostgreSQL local real. Em
`backend/app/sources/source_registry.py`: `block_source`/`unblock_source
(source_id, origin, reason, responsible=None)` — gravam a
`BlacklistEntry` na mesma transação da mudança de `is_blocked`;
`SourceBlacklistStateError` para bloquear já bloqueada ou desbloquear
não bloqueada. `list_blacklist_entries(source_id)` lê o histórico.

Mecânico: nenhuma checagem de quem pode chamar. Decidir *quando*
bloquear automaticamente é TASK-065; impor que só `ADMIN` pode
desbloquear é TASK-066 — nenhuma das duas implementada aqui.

14 testes novos (4 unitários de validação de `reason` + 10 de integração
real). Suíte completa: 522/522 testes aprovados.
