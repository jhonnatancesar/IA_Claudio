# TASK-020 — Criar modelo de Execution

Status: **Concluída em 2026-08-16**

## Objetivo

Criar modelo de Execution, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Orquestração") e `docs/ORCHESTRATOR.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Orquestração" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ORCHESTRATOR.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-019 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ORCHESTRATOR.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do orquestrador para este passo do ciclo de execução, incluindo casos de erro/limite; teste de integração cobrindo o ciclo completo quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/ORCHESTRATOR.md`, `docs/tasks/README.md`, `backend/app/orchestrator/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/orchestrator/execution.py`:
`Execution` (dataclass), `ExecutionStatus`
(`PENDING`/`RUNNING`/`COMPLETED`/`FAILED`, mesmo conjunto da fila —
`docs/QUEUE.md`), `InvalidExecutionStateError`. Transições válidas:
`start()`, `add_step()` (só `RUNNING`), `complete(result)`, `fail(error)`
(qualquer estado não-terminal, inclusive direto de `PENDING`). Sem
`CANCELLED` (TASK-030), sem política (TASK-022), sem execução real
(`ExecutionOrchestrator`, TASK-023). 15 testes unitários novos, incluindo um
cobrindo o ciclo completo (criar → iniciar → etapas → concluir). Suíte
completa: 161/161 testes aprovados.
