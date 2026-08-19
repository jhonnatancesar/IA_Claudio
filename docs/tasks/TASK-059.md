# TASK-059 — Criar cadastro de fontes

Status: **Concluída em 2026-08-19**

## Objetivo

Criar cadastro de fontes, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Fontes") e `docs/TRUST_GUARDRAILS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fontes" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TRUST_GUARDRAILS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-058 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TRUST_GUARDRAILS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de fontes/reputação/blacklist para este comportamento específico, conforme docs/TESTING.md.

## Documentação afetada

`docs/TRUST_GUARDRAILS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. Criado schema
`backend/app/db/migrations/0010_sources.sql` (tabela `sources`: `id`,
`identifier` único, `created_at`), aplicado no PostgreSQL local real.
Criado `backend/app/sources/source_registry.py`: `Source` (dataclass),
`register_source(identifier)` — idempotente por `identifier`
(`ON CONFLICT ... DO UPDATE ... RETURNING`, devolve a fonte existente em
vez de duplicar), `get_source(source_id)`,
`get_source_by_identifier(identifier)`.

Só a identidade da fonte — tipo `PRIMARY`/`SECONDARY`/`UNKNOWN`
(TASK-060), reputação (TASK-061 em diante) e blacklist (TASK-064 em
diante) não são desta TASK.

7 testes novos (2 unitários de validação + 5 de integração real). Suíte
completa: 482/482 testes aprovados.
