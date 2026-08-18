# TASK-032 — Implementar volatilidade VOLATILE/NON_VOLATILE

Status: **Concluída em 2026-08-16**

## Objetivo

Implementar volatilidade VOLATILE/NON_VOLATILE, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Confiança e guardrails") e `docs/TRUST_GUARDRAILS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Confiança e guardrails" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TRUST_GUARDRAILS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-031 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TRUST_GUARDRAILS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de confiança/guardrails, incluindo casos de bloqueio (LOW), revalidação (VOLATILE) e ambiguidade; testes explícitos contra alucinação quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/TRUST_GUARDRAILS.md`, `docs/tasks/README.md`, `backend/app/confidence/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/confidence/volatility.py`:
`Volatility` (`VOLATILE`/`NON_VOLATILE`), `requires_revalidation(volatility)`
— `True` só para `VOLATILE`, independente de confiança. Seção 13.2 da
especificação é curta (só essa regra), então a implementação ficou
proporcionalmente pequena, de propósito. Onde a volatilidade é registrada
(Knowledge Tool) e onde é aplicada como guardrail antes de responder
(TASK-035) não são desta TASK.

5 testes unitários novos. Suíte completa: 263/263 testes aprovados.
