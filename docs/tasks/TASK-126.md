# TASK-126 — Implementar backup manual

Status: Pendente

## Objetivo

Implementar backup manual, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Operação") e `docs/BACKUP_RESTORE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Operação" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/BACKUP_RESTORE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-125 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/BACKUP_RESTORE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Teste de integração do fluxo operacional (manutenção, reinício, backup, restore ou updater, conforme o caso), incluindo o caminho de falha/rollback quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/BACKUP_RESTORE.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)
