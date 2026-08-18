# TASK-037 — Criar ContextManager

Status: **Concluída em 2026-08-16**

## Objetivo

Criar ContextManager, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Contexto") e `docs/ORCHESTRATOR.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Contexto" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ORCHESTRATOR.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-036 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ORCHESTRATOR.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do ContextManager para este comportamento (rastreamento, correção, troca de assunto ou aviso de janela), conforme docs/TESTING.md.

## Documentação afetada

`docs/ORCHESTRATOR.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/context/context_manager.py`:
`ContextManager` (dataclass) — `conversation_id`, `active_topic`,
`recent_entities`, `current_objective`, `recent_actions`,
`implicit_references`, `corrections`, todos vazios/`None` até as TASKs
seguintes preenchê-los de fato. `ContextManager.new(conversation_id)` cria a
instância vazia, mesmo padrão de `Execution.new()` (TASK-020/021). Só o
modelo de dados nasce aqui — active topic e troca de assunto (TASK-038/
TASK-041), rastreamento de entidades/referências implícitas (TASK-039),
correção de contexto (TASK-040) e monitor de janela de contexto/aviso em
80% (TASK-042/TASK-043) são comportamento de TASKs futuras, não
implementado nesta TASK.

4 testes unitários novos. Suíte completa: 290/290 testes aprovados.
