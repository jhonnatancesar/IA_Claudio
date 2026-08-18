# TASK-044 — Criar modelo de memória persistente

Status: **Concluída em 2026-08-18**

## Objetivo

Criar modelo de memória persistente, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Memória") e `docs/MEMORY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Memória" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/MEMORY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-043 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/MEMORY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de memória (persistência, busca, relevância, retenção ou auditoria de remoção, conforme o caso); teste de integração com o banco quando a TASK persistir dados, conforme docs/TESTING.md.

## Documentação afetada

`docs/MEMORY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Criado schema `backend/app/db/migrations/0003_memory.sql`
(tabela `memories`: `id`, `owner_type` `USER`/`APPLICATION`, `owner_id`,
`content`, `created_at`, `updated_at`), aplicado no PostgreSQL local real.
Criado `backend/app/memory/memory_model.py`: `Memory` (dataclass),
`save_memory(owner_type, owner_id, content)`, `get_memory(memory_id)` —
persistência real via `psycopg`, mesmo padrão de `app.auth.users`
(TASK-009). `InvalidOwnerTypeError` para `owner_type` desconhecido.

`owner_type`/`owner_id` já existem no schema, mas garantir que uma consulta
só devolve memórias do próprio dono (separação de fato) é TASK-045, não
implementado aqui — `get_memory` busca só pelo `id`. Memory Tool
(TASK-046), busca estruturada (TASK-047), relevância/frequência/last_used
(TASK-048), retenção (TASK-049), limite fixo (TASK-050) e auditoria de
remoção (TASK-051) não são desta TASK.

4 testes de integração novos (persistência real contra o PostgreSQL local
— sem teste unitário separado, mesmo padrão de `app.auth.users`). Suíte
completa: 327/327 testes aprovados.
