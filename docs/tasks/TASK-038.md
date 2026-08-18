# TASK-038 — Criar active topic

Status: **Concluída em 2026-08-16**

## Objetivo

Criar active topic, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Contexto") e `docs/ORCHESTRATOR.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Contexto" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ORCHESTRATOR.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-037 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ORCHESTRATOR.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do ContextManager para este comportamento (rastreamento, correção, troca de assunto ou aviso de janela), conforme docs/TESTING.md.

## Documentação afetada

`docs/ORCHESTRATOR.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-16. Acrescentado `ContextManager.set_active_topic(topic)`
em `backend/app/context/context_manager.py`: define o assunto principal da
conversa, substituindo qualquer assunto anterior — "a V1 mantém um assunto
principal por vez" (seção 9 da especificação), não uma lista/histórico.
Levanta `ValueError` para `topic` vazio. Decidir *quando* uma troca de
assunto real aconteceu (e então chamar este método, limpando referências
antigas) é TASK-041, não implementado aqui.

4 testes unitários novos. Suíte completa: 294/294 testes aprovados.
