# TASK-096 — Implementar política HTTPS

Status: Pendente

## Objetivo

Implementar política HTTPS, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "APIs e arquivos") e `docs/SECURITY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "APIs e arquivos" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/SECURITY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-095 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/SECURITY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários da ferramenta correspondente (API Tool, File Tool ou Database Tool), incluindo casos fora do contrato (devem ser bloqueados pelo orquestrador), conforme docs/TESTING.md.

## Documentação afetada

`docs/SECURITY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)
