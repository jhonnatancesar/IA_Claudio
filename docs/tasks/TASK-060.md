# TASK-060 — Implementar PRIMARY/SECONDARY/UNKNOWN

Status: **Concluída em 2026-08-19**

## Objetivo

Implementar PRIMARY/SECONDARY/UNKNOWN, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Fontes") e `docs/TRUST_GUARDRAILS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fontes" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TRUST_GUARDRAILS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-059 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TRUST_GUARDRAILS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de fontes/reputação/blacklist para este comportamento específico, conforme docs/TESTING.md.

## Documentação afetada

`docs/TRUST_GUARDRAILS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. Criado schema
`backend/app/db/migrations/0011_source_type.sql` (coluna `source_type`
em `sources`, `CHECK` restringindo a `PRIMARY`/`SECONDARY`/`UNKNOWN`,
padrão `UNKNOWN`), aplicado no PostgreSQL local real. Em
`backend/app/sources/source_registry.py`: `SourceType` (enum),
`register_source` aceita `source_type` opcional (padrão `UNKNOWN`),
`set_source_type(source_id, source_type)` reclassifica uma fonte já
registrada (`SourceNotFoundError` se não existir).

Tipo e reputação são conceitos independentes — reputação de fato é
TASK-061 em diante, não implementada aqui.

5 testes novos (1 unitário de enum + 4 de integração real). Suíte
completa: 487/487 testes aprovados.
