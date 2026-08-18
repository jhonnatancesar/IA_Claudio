# TASK-036 — Implementar tratamento de ambiguidade

Status: **Concluída em 2026-08-16**

## Objetivo

Implementar tratamento de ambiguidade, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Confiança e guardrails") e `docs/TRUST_GUARDRAILS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Confiança e guardrails" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TRUST_GUARDRAILS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-035 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TRUST_GUARDRAILS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de confiança/guardrails, incluindo casos de bloqueio (LOW), revalidação (VOLATILE) e ambiguidade; testes explícitos contra alucinação quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/TRUST_GUARDRAILS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-16. Criado
`backend/app/confidence/ambiguity_guardrail.py`:
`ensure_ambiguity_resolved_before_response(is_ambiguous,
clarification_requested)`, que levanta `ClaudiaoError` (novo código `4008`,
`UNRESOLVED_AMBIGUITY`) quando há ambiguidade real sem pergunta de
esclarecimento — mesmo padrão de guarda isolada de `response_guardrail.py`
(TASK-034) e `revalidation_guardrail.py` (TASK-035). O protocolo (TASK-016)
não tem `action` própria de "pergunta"; perguntar é um `RESPOND` cujo
`reason` pergunta em vez de concluir, por isso a guarda recebe
`clarification_requested` como booleano explícito em vez de tentar
distingui-lo do conteúdo da resposta. Avaliar de fato se há ambiguidade
(`ContextManager`, TASK-037 em diante) e acionar esta guarda no fluxo real
do orquestrador não são desta TASK.

Com esta TASK, o bloco "Confiança e guardrails" (TASK-031 a TASK-036) está
completo.

3 testes unitários novos. Suíte completa: 286/286 testes aprovados.
