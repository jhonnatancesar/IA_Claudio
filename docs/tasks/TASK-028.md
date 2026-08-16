# TASK-028 — Implementar max_steps

Status: **Concluída em 2026-08-16**

## Objetivo

Implementar max_steps, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Orquestração") e `docs/ORCHESTRATOR.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Orquestração" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ORCHESTRATOR.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-027 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ORCHESTRATOR.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do orquestrador para este passo do ciclo de execução, incluindo casos de erro/limite; teste de integração cobrindo o ciclo completo quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/ORCHESTRATOR.md`, `docs/ERROR_CATALOG.md`, `docs/tasks/README.md`,
`backend/app/orchestrator/README.md`

## Encerramento

Concluída em 2026-08-16. `ExecutionOrchestrator.run_step` (TASK-023) passou
a checar `execution.step_count >= policy.max_steps` **antes** de chamar o
modelo — se o limite já foi atingido, marca a execução `FAILED` e levanta
`ClaudiaoError` com o novo código `4004` (`MAX_STEPS_EXCEEDED`, HTTP 429),
sem gastar uma chamada ao provider. `run_until_response` (TASK-026) herda o
limite automaticamente, por chamar `run_step` em loop.

5 testes unitários novos (limite já atingido rejeita nova etapa sem chamar o
provider, loop `run_until_response` para exatamente em `max_steps` etapas
com um provider que nunca decide `RESPOND`, `max_steps` padrão de 10
respeitado, conclusão normal abaixo do limite). Suíte completa: 222/222
testes aprovados.
