# TASK-033 — Implementar confidence engine do orquestrador

Status: **Concluída em 2026-08-16**

## Objetivo

Implementar confidence engine do orquestrador, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Confiança e guardrails") e `docs/TRUST_GUARDRAILS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Confiança e guardrails" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TRUST_GUARDRAILS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-032 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TRUST_GUARDRAILS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de confiança/guardrails, incluindo casos de bloqueio (LOW), revalidação (VOLATILE) e ambiguidade; testes explícitos contra alucinação quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/TRUST_GUARDRAILS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/confidence/confidence_engine.py`:
`EvidenceStrength` (`NONE`/`WEAK`/`STRONG`, resumo abstrato de evidência
externa), `calculate_final_confidence(model_confidence, evidence)`
implementando a seção 13.3 (`HIGH` rebaixado para `MEDIUM` com evidência
`WEAK`/`NONE`; `MEDIUM` elevado para `HIGH` com evidência `STRONG`; `LOW`
nunca é elevado) e `calculate_final_confidence_for_execution(execution,
evidence)`, atalho sobre `get_model_confidence` (TASK-031). Reputação real de
fontes (TASK-059+) e evidências reais de pesquisa (TASK-088+) não existem
ainda — o motor recebe `EvidenceStrength` já calculado por quem chama, sem
acoplar a essas TASKs futuras. Contradições (dependem de conhecimento
confirmado/provisório, TASK-052+) não têm representação nesta TASK. Aplicar
a confiança final como guardrail de bloqueio de resposta é TASK-034.

12 testes unitários novos. Suíte completa: 275/275 testes aprovados.
