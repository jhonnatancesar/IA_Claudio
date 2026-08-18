# TASK-031 — Implementar confiança LOW/MEDIUM/HIGH do modelo

Status: **Concluída em 2026-08-16**

## Objetivo

Implementar confiança LOW/MEDIUM/HIGH do modelo, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Confiança e guardrails") e `docs/TRUST_GUARDRAILS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Confiança e guardrails" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TRUST_GUARDRAILS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-030 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TRUST_GUARDRAILS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de confiança/guardrails, incluindo casos de bloqueio (LOW), revalidação (VOLATILE) e ambiguidade; testes explícitos contra alucinação quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/TRUST_GUARDRAILS.md`, `docs/tasks/README.md`, `backend/app/confidence/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/confidence/model_confidence.py`:
`CONFIDENCE_ORDER` (ordem explícita `LOW < MEDIUM < HIGH`), `is_at_least()`,
`get_model_confidence(execution)` (lê a confiança da etapa `RESPOND`,
`NoRespondStepError` se ainda não houver uma). Reaproveita `Confidence` de
`app.llm.protocol` (TASK-016), sem duplicar. Cálculo da confiança final
(Confidence Engine) é TASK-033; guardrails que agem sobre a confiança são
TASK-034/TASK-035/TASK-036 — nenhum implementado aqui.

10 testes unitários novos (ordem, `is_at_least` parametrizado, leitura da
confiança em execuções com e sem `RESPOND`, ignorando etapas `USE_TOOL`
intermediárias). Suíte completa: 258/258 testes aprovados.
