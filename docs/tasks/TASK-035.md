# TASK-035 — Implementar regra obrigatória para informação volátil

Status: **Concluída em 2026-08-16**

## Objetivo

Implementar regra obrigatória para informação volátil, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Confiança e guardrails") e `docs/TRUST_GUARDRAILS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Confiança e guardrails" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TRUST_GUARDRAILS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-034 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TRUST_GUARDRAILS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de confiança/guardrails, incluindo casos de bloqueio (LOW), revalidação (VOLATILE) e ambiguidade; testes explícitos contra alucinação quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/TRUST_GUARDRAILS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-16. Criado
`backend/app/confidence/revalidation_guardrail.py`:
`ensure_volatile_information_revalidated(volatility, was_revalidated)`, que
levanta `ClaudiaoError` (novo código `4007`,
`VOLATILE_INFORMATION_NOT_REVALIDATED`) quando `requires_revalidation`
(TASK-032) exige revalidação e ela não aconteceu. `NON_VOLATILE` e
`VOLATILE` já revalidada passam livres — segue o mesmo padrão de guarda
isolada de `response_guardrail.py` (TASK-034). Executar a revalidação de
fato (Knowledge Tool, TASK-052+) e acionar esta guarda no fluxo real do
orquestrador não são desta TASK.

3 testes unitários novos. Suíte completa: 282/282 testes aprovados.
