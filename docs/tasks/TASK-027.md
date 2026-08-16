# TASK-027 — Implementar replanejamento completo

Status: **Concluída em 2026-08-16**

## Objetivo

Implementar replanejamento completo, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Orquestração") e `docs/ORCHESTRATOR.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Orquestração" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ORCHESTRATOR.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-026 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ORCHESTRATOR.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do orquestrador para este passo do ciclo de execução, incluindo casos de erro/limite; teste de integração cobrindo o ciclo completo quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/ORCHESTRATOR.md`, `docs/tasks/README.md`, `backend/app/orchestrator/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/orchestrator/replanner.py`:
`replan(orchestrator, old_execution, objective, model)` — encerra a execução
atual (`fail()`, único estado terminal disponível para isso hoje — um
estado dedicado pode fazer mais sentido quando `CANCELLED` existir,
TASK-030) e cria uma execução nova (`execution_id` novo, mesmo `origin`) via
`plan_initial_step` (TASK-024), garantindo que o novo plano passe pelas
mesmas regras do plano inicial, incluindo `validate_plan` (TASK-025).
`CannotReplanFinishedExecutionError` para execução já terminal. Histórico da
execução antiga preservado, só marcada como encerrada.

5 testes unitários novos (descarta e cria nova, preserva histórico antigo,
rejeita replanejar execução já concluída/já falhada, novo plano passa pela
validação de plano). Suíte completa: 217/217 testes aprovados.
