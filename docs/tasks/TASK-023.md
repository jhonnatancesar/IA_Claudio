# TASK-023 — Criar ExecutionOrchestrator

Status: **Concluída em 2026-08-16**

## Objetivo

Criar ExecutionOrchestrator, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Orquestração") e `docs/ORCHESTRATOR.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Orquestração" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ORCHESTRATOR.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-022 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ORCHESTRATOR.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do orquestrador para este passo do ciclo de execução, incluindo casos de erro/limite; teste de integração cobrindo o ciclo completo quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/ORCHESTRATOR.md`, `docs/tasks/README.md`, `backend/app/orchestrator/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/orchestrator/orchestrator.py`:
`ExecutionOrchestrator(provider, policy)` com `run_step(execution, objective,
model)` — primeira peça que liga de verdade `LocalLLMProvider`,
`compose_prompt`, `validate_step` e `Execution` num passo real (inicia a
execução, compõe o prompt com histórico, chama o modelo, valida a resposta,
registra a etapa, conclui se `RESPOND`, marca `FAILED` em qualquer falha).
`ExecutionPolicy` guardada mas ainda não aplicada — isso fica para TASK-028
em diante.

10 testes unitários com provider fake (conclusão em `RESPOND`, execução
segue `RUNNING` em `USE_TOOL`, histórico registrado e propagado a chamadas
seguintes, falha do runtime e do protocolo marcam `FAILED` corretamente) + 1
teste de integração real contra o Ollama local (modelo inexistente falha a
execução corretamente, sem travar nem vazar outra exceção — confirmado
rodando de verdade, não pulado). Suíte completa: 190/190 testes aprovados.
