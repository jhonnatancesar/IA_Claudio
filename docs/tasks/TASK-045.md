# TASK-045 — Separar memória por usuário/aplicação

Status: **Concluída em 2026-08-18**

## Objetivo

Separar memória por usuário/aplicação, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Memória") e `docs/MEMORY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Memória" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/MEMORY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-044 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/MEMORY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de memória (persistência, busca, relevância, retenção ou auditoria de remoção, conforme o caso); teste de integração com o banco quando a TASK persistir dados, conforme docs/TESTING.md.

## Documentação afetada

`docs/MEMORY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Acrescentado `list_memories_for_owner(owner_type,
owner_id)` em `backend/app/memory/memory_model.py`: garante de fato que
"usuários diferentes têm memórias separadas" (seção 11) — filtra por
`owner_type`/`owner_id` exatos, nunca mistura memórias de outro dono nem de
outro `owner_type` (uma aplicação e um usuário com o mesmo `owner_id` têm
listas independentes). Ordem: mais recente primeiro (`created_at DESC`).
Levanta `InvalidOwnerTypeError` para `owner_type` desconhecido.

4 testes de integração novos (persistência real). Suíte completa:
331/331 testes aprovados.
