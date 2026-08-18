# TASK-040 — Implementar correção de contexto

Status: **Concluída em 2026-08-18**

## Objetivo

Implementar correção de contexto, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Contexto") e `docs/ORCHESTRATOR.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Contexto" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ORCHESTRATOR.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-039 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ORCHESTRATOR.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do ContextManager para este comportamento (rastreamento, correção, troca de assunto ou aviso de janela), conforme docs/TESTING.md.

## Documentação afetada

`docs/ORCHESTRATOR.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Acrescentado `ContextManager.record_correction
(correction)` em `backend/app/context/context_manager.py`: registra uma
correção feita pelo usuário em `corrections`, em ordem cronológica — só o
histórico bruto; reinterpretar `active_topic`/`current_objective` a partir
do conteúdo da correção exigiria entendê-lo, fora do escopo desta TASK.
Levanta `ValueError` para correção vazia.

3 testes unitários novos. Suíte completa: 306/306 testes aprovados.
