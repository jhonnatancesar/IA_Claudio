# TASK-063 — Criar histórico de reputação

Status: **Concluída em 2026-08-19**

## Objetivo

Criar histórico de reputação, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Fontes") e `docs/TRUST_GUARDRAILS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fontes" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TRUST_GUARDRAILS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-062 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TRUST_GUARDRAILS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de fontes/reputação/blacklist para este comportamento específico, conforme docs/TESTING.md.

## Documentação afetada

`docs/TRUST_GUARDRAILS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. Criado schema
`backend/app/db/migrations/0013_source_reputation_history.sql` (tabela
`source_reputation_history`: `source_id` com `ON DELETE CASCADE`,
`previous_reputation`, `new_reputation`, `changed_at`), aplicado no
PostgreSQL local real. `set_source_reputation`
(`backend/app/sources/source_registry.py`) agora grava, na mesma
transação, uma linha de histórico sempre que a reputação muda de fato —
chamar com o mesmo valor já vigente não grava nada. Nova
`ReputationHistoryEntry`/`list_reputation_history(source_id)` lê o
histórico, mais antigo primeiro. `update_source_reputation` (TASK-062)
ganha histórico automaticamente, sem mudança própria.

6 testes novos, todos de integração real (persistência de histórico e
não gravação em no-op). Suíte completa: 508/508 testes aprovados.
