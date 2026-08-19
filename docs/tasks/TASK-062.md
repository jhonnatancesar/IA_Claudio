# TASK-062 — Implementar atualização de reputação

Status: **Concluída em 2026-08-19**

## Objetivo

Implementar atualização de reputação, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Fontes") e `docs/TRUST_GUARDRAILS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fontes" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TRUST_GUARDRAILS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-061 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TRUST_GUARDRAILS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de fontes/reputação/blacklist para este comportamento específico, conforme docs/TESTING.md.

## Documentação afetada

`docs/TRUST_GUARDRAILS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. Criado `backend/app/sources/reputation_rule.py`:
`update_reputation(current, was_accurate)` (função pura) — resultado
incorreto rebaixa um degrau (`HIGH → MEDIUM → LOW`, permanece `LOW`),
resultado correto eleva um degrau (`LOW → MEDIUM → HIGH`, permanece
`HIGH`); "um degrau por vez" é o critério mais simples e defensável, já
que a especificação não detalha a magnitude do ajuste.
`update_source_reputation(source_id, was_accurate)` busca a fonte,
calcula a nova reputação e só grava (`set_source_reputation`, TASK-061)
se realmente mudar.

Histórico de cada mudança (quando, por quê) é TASK-063, não implementado
aqui.

10 testes novos (6 unitários de `update_reputation`, função pura + 4 de
integração real). Suíte completa: 502/502 testes aprovados.
