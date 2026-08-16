# TASK-050 — Implementar limite fixo de memória

Status: Pendente

## Objetivo

Implementar limite fixo de memória, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Memória") e `docs/MEMORY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Memória" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/MEMORY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-049 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/MEMORY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de memória (persistência, busca, relevância, retenção ou auditoria de remoção, conforme o caso); teste de integração com o banco quando a TASK persistir dados, conforme docs/TESTING.md.

## Documentação afetada

`docs/MEMORY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)
