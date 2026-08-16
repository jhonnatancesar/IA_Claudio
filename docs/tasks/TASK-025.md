# TASK-025 — Implementar validação de plano

Status: **Concluída em 2026-08-16**

## Objetivo

Implementar validação de plano, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Orquestração") e `docs/ORCHESTRATOR.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Orquestração" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ORCHESTRATOR.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-024 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ORCHESTRATOR.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do orquestrador para este passo do ciclo de execução, incluindo casos de erro/limite; teste de integração cobrindo o ciclo completo quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/ORCHESTRATOR.md`, `docs/ERROR_CATALOG.md`, `docs/tasks/README.md`,
`backend/app/orchestrator/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/orchestrator/plan_validator.py`:
`validate_plan(step, execution, policy)` — checa `execution_id` da etapa
contra a execução (código `4002`) e `WEB_SEARCH` contra
`ExecutionPolicy.web_search_allowed` (código `4003`). Integrado em
`ExecutionOrchestrator.run_step` (TASK-023), logo depois da validação
sintática do protocolo. 5 testes unitários novos do validador + 2 de
regressão no orquestrador (rejeita/aceita `WEB_SEARCH` conforme a política).
Ajustados os testes antigos da TASK-023 que usavam `WEB_SEARCH` sem
autorização explícita na política (passaram a falhar corretamente com a
nova validação — não é regressão, é o comportamento certo). Suíte completa:
201/201 testes aprovados.
