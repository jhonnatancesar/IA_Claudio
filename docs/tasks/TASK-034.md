# TASK-034 — Implementar bloqueio de resposta conclusiva em LOW

Status: **Concluída em 2026-08-16**

## Objetivo

Implementar bloqueio de resposta conclusiva em LOW, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Confiança e guardrails") e `docs/TRUST_GUARDRAILS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Confiança e guardrails" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TRUST_GUARDRAILS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-033 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TRUST_GUARDRAILS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de confiança/guardrails, incluindo casos de bloqueio (LOW), revalidação (VOLATILE) e ambiguidade; testes explícitos contra alucinação quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/TRUST_GUARDRAILS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/confidence/response_guardrail.py`:
`ensure_conclusive_response_allowed(final_confidence)`, que levanta
`ClaudiaoError` (novo código `4006`, `LOW_CONFIDENCE_BLOCKED`) quando a
confiança final for `LOW`, conforme a seção 13.3 — nesse nível o Claudião
não pode apresentar conclusão como fato. `MEDIUM` e `HIGH` passam livres;
sinalizar incerteza em `MEDIUM` fica para quem monta a resposta. A guarda
recebe a confiança final já calculada (Confidence Engine, TASK-033) — onde
ela é efetivamente acionada no fluxo real do orquestrador, antes de uma
resposta chegar ao usuário/aplicação, não é desta TASK.

3 testes unitários novos. Suíte completa: 278/278 testes aprovados.
