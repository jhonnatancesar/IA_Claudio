# TASK-041 — Implementar detecção de troca de assunto

Status: **Concluída em 2026-08-18**

## Objetivo

Implementar detecção de troca de assunto, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Contexto") e `docs/ORCHESTRATOR.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Contexto" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ORCHESTRATOR.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-040 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ORCHESTRATOR.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do ContextManager para este comportamento (rastreamento, correção, troca de assunto ou aviso de janela), conforme docs/TESTING.md.

## Documentação afetada

`docs/ORCHESTRATOR.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Acrescentado `ContextManager.detect_topic_switch
(new_topic)` em `backend/app/context/context_manager.py`: decide *quando*
`set_active_topic` (TASK-038) deve trocar de fato o assunto — critério mais
simples e defensável, já que a especificação (seção 9) não detalha um:
`new_topic` diferente do `active_topic` atual já conta como troca real.
Quando detecta troca, aplica (`set_active_topic`) e limpa
`recent_entities`/`implicit_references` — "limpa referências antigas
quando houver mudança real de tópico". Retorna `True`/`False` conforme
trocou ou não; levanta `ValueError` para `new_topic` vazio. Decidir se dois
textos diferentes descrevem o "mesmo assunto" (paráfrase, sinônimo)
exigiria interpretação semântica, fora do escopo desta TASK.

4 testes unitários novos. Suíte completa: 311/311 testes aprovados.
