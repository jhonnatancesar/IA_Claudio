# TASK-043 — Implementar aviso em 80%

Status: **Concluída em 2026-08-18**

## Objetivo

Implementar aviso em 80%, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Contexto") e `docs/ORCHESTRATOR.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Contexto" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ORCHESTRATOR.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-042 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ORCHESTRATOR.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do ContextManager para este comportamento (rastreamento, correção, troca de assunto ou aviso de janela), conforme docs/TESTING.md.

## Documentação afetada

`docs/ORCHESTRATOR.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Acrescentado `ContextWindowMonitor.requires_warning
(tokens_used, threshold=DEFAULT_WARNING_THRESHOLD)` em
`backend/app/context/context_window.py`, com a nova constante
`DEFAULT_WARNING_THRESHOLD = 0.8`: `True` a partir de 80% de uso da janela
— "aviso preventivo, discreto, ao atingir 80% de uso" (seção 9). Continua
`True` mesmo além de 100% de uso. Só o sinal booleano — como o aviso é
efetivamente mostrado ao usuário é responsabilidade de quem consome esse
sinal (painel/API), fora do escopo desta TASK.

Com esta TASK, o bloco "Contexto" (TASK-037 a TASK-043) está completo.

5 testes unitários novos. Suíte completa: 323/323 testes aprovados.
