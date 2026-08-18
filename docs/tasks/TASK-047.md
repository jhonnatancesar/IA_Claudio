# TASK-047 — Implementar busca estruturada de memória

Status: **Concluída em 2026-08-18**

## Objetivo

Implementar busca estruturada de memória, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Memória") e `docs/MEMORY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Memória" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/MEMORY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-046 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/MEMORY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de memória (persistência, busca, relevância, retenção ou auditoria de remoção, conforme o caso); teste de integração com o banco quando a TASK persistir dados, conforme docs/TESTING.md.

## Documentação afetada

`docs/MEMORY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Acrescentado `search_memories(owner_type,
owner_id, query)` em `backend/app/memory/memory_model.py`: busca
estruturada por conteúdo (`content ILIKE '%query%'`, sem diferenciar
maiúsculas/minúsculas), dentro do escopo do dono (mesma garantia de
separação da TASK-045), mais recente primeiro. Sem ranking por relevância
— isso é TASK-048. Exposta na Memory Tool (`backend/app/tools/memory_tool.py`)
como nova operação `"SEARCH"` (exige `owner_type`/`owner_id`/`query`).

12 testes novos (8 unitários/integração de `search_memories` +
`execute_memory_tool`). Suíte completa: 353/353 testes aprovados.
