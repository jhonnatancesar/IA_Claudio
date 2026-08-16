# TASK-119 — Gestão de cotas

Status: Pendente

## Objetivo

Gestão de cotas, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Administração") e `docs/PANEL.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Administração" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/PANEL.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-118 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/PANEL.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários/integração do painel administrativo para esta gestão específica, incluindo o fluxo de reautenticação em ações críticas quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/PANEL.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)
