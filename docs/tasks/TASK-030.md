# TASK-030 — Implementar cancelamento

Status: **Concluída em 2026-08-16**

## Objetivo

Implementar cancelamento, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Orquestração") e `docs/ORCHESTRATOR.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Orquestração" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ORCHESTRATOR.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-029 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ORCHESTRATOR.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do orquestrador para este passo do ciclo de execução, incluindo casos de erro/limite; teste de integração cobrindo o ciclo completo quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/ORCHESTRATOR.md`, `docs/tasks/README.md`, `backend/app/orchestrator/README.md`

## Encerramento

Concluída em 2026-08-16. Adicionado o estado `ExecutionStatus.CANCELLED`
(previsto desde a TASK-020) e `Execution.cancel(reason)` — mesmo padrão de
`fail()`, qualquer estado não-terminal pode ser cancelado. Criado
`backend/app/orchestrator/cancellation.py`: `CancellationToken`
(cooperativo, sem threads/async) e `ExecutionCancelledError` (não é
`ClaudiaoError` — cancelamento não é uma falha de domínio).
`ExecutionOrchestrator.run_step`/`run_until_response` ganharam o parâmetro
opcional `cancellation_token`, checado antes de qualquer chamada ao modelo
(cobre cancelamento externo e interno pelo mesmo mecanismo);
`plan_initial_step` (TASK-024) e `replan` (TASK-027) repassam o token
adiante. `CANCELLED`, sendo terminal, também passou a bloquear
replanejamento.

O erro JSON específico de timeout de aplicação (seção 26 da especificação)
continua sendo escopo da TASK-071 — aqui só a primitiva de cancelamento do
orquestrador.

10 testes unitários de `Execution.cancel()`/`CancellationToken` + 4 de
integração no orquestrador (cancelamento antes de chamar o modelo,
cancelamento no meio do loop via `tool_executor`, `plan_initial_step`
repassando o token, `replan` rejeitando execução já cancelada). Suíte
completa: 247/247 testes aprovados.

**Com esta TASK, o bloco "Orquestração" (TASK-020 a TASK-030) está
completo.**
