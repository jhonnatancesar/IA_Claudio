# TASK-042 — Implementar monitor de janela de contexto

Status: **Concluída em 2026-08-18**

## Objetivo

Implementar monitor de janela de contexto, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Contexto") e `docs/ORCHESTRATOR.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Contexto" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ORCHESTRATOR.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-041 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ORCHESTRATOR.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do ContextManager para este comportamento (rastreamento, correção, troca de assunto ou aviso de janela), conforme docs/TESTING.md.

## Documentação afetada

`docs/ORCHESTRATOR.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Criado `backend/app/context/context_window.py`:
`ContextWindowMonitor(capacity)` (dataclass imutável), `usage_ratio
(tokens_used)` (fração usada da janela, podendo passar de `1.0`) e
`is_full(tokens_used)`. `InvalidContextWindowError` para `capacity`
não positiva ou `tokens_used` negativo. O painel (TASK-100+) e a
persistência de configuração ainda não existem, por isso `capacity` é
recebida como parâmetro explícito de quem cria o monitor. Emitir o aviso
preventivo ao atingir 80% de uso é TASK-043, não implementado aqui.

6 testes unitários novos. Suíte completa: 318/318 testes aprovados.
