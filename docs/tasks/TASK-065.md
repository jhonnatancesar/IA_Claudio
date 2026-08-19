# TASK-065 — Implementar bloqueio automático

Status: **Concluída em 2026-08-19**

## Objetivo

Implementar bloqueio automático, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Fontes") e `docs/TRUST_GUARDRAILS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fontes" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TRUST_GUARDRAILS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-064 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TRUST_GUARDRAILS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de fontes/reputação/blacklist para este comportamento específico, conforme docs/TESTING.md.

## Documentação afetada

`docs/TRUST_GUARDRAILS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. Criado `backend/app/sources/auto_block_rule.py`:
`is_eligible_for_auto_block(reputation)` (função pura: hoje só
`reputation == LOW`) e `auto_block_after_validation(source_id,
was_accurate)`, que encadeia `update_source_reputation` (TASK-062) com
`block_source` (TASK-064, `origin=AGENT`) quando a reputação cai para
`LOW` e a fonte ainda não está bloqueada — a especificação não detalha
qual validação dispara o bloqueio automático, e a queda de reputação
para `LOW` já construída na TASK-062 é o gatilho mais simples e
defensável.

"Bloqueio automático gera alerta no painel" não é desta TASK — o painel
ainda não existe (TASK-081 em diante).

7 testes novos (3 unitários de `is_eligible_for_auto_block`, função pura
+ 4 de integração real). Suíte completa: 529/529 testes aprovados.
