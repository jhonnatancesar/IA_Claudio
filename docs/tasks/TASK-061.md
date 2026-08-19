# TASK-061 — Implementar reputação LOW/MEDIUM/HIGH

Status: **Concluída em 2026-08-19**

## Objetivo

Implementar reputação LOW/MEDIUM/HIGH, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Fontes") e `docs/TRUST_GUARDRAILS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fontes" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TRUST_GUARDRAILS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-060 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TRUST_GUARDRAILS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de fontes/reputação/blacklist para este comportamento específico, conforme docs/TESTING.md.

## Documentação afetada

`docs/TRUST_GUARDRAILS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. Criado schema
`backend/app/db/migrations/0012_source_reputation.sql` (coluna
`reputation` em `sources`, `CHECK` restringindo a `LOW`/`MEDIUM`/`HIGH`,
padrão `MEDIUM`), aplicado no PostgreSQL local real. Em
`backend/app/sources/source_registry.py`: `SourceReputation` (enum),
`register_source` aceita `reputation` opcional (padrão `MEDIUM`),
`set_source_reputation(source_id, reputation)` aplica a troca mecânica
(`SourceNotFoundError` se não existir).

A regra que decide *quando* rebaixar/elevar a reputação com base em
dados corretos/errados apresentados é a atualização de reputação,
TASK-062, não implementada aqui.

5 testes novos (1 unitário de enum + 4 de integração real). Suíte
completa: 492/492 testes aprovados.
