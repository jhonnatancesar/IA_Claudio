# TASK-022 — Criar ExecutionPolicy

Status: **Concluída em 2026-08-16**

## Objetivo

Criar ExecutionPolicy, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Orquestração") e `docs/ORCHESTRATOR.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Orquestração" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ORCHESTRATOR.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-021 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ORCHESTRATOR.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do orquestrador para este passo do ciclo de execução, incluindo casos de erro/limite; teste de integração cobrindo o ciclo completo quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/ORCHESTRATOR.md`, `docs/tasks/README.md`, `backend/app/policies/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/policies/execution_policy.py`
(no módulo `policies/` dedicado, não em `orchestrator/` — corrigido durante a
própria TASK após um primeiro rascunho no lugar errado): `ExecutionPolicy`
(dataclass imutável: `web_search_allowed`, `max_steps` padrão `10`,
`timeout_seconds`), `InvalidExecutionPolicyError`, fábricas `for_chat()` (sem
timeout fixo) e `for_application(timeout_seconds=...)` (timeout obrigatório).
14 testes unitários novos. Suíte completa: 180/180 testes aprovados.
