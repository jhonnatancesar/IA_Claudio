# TASK-075 — Persistir fila no PostgreSQL

Status: **Concluída em 2026-08-19**

## Objetivo

Persistir fila no PostgreSQL, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Fila") e `docs/QUEUE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fila" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/QUEUE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-074 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/QUEUE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários e de integração da fila (estados, persistência, retenção), conforme docs/TESTING.md.

## Documentação afetada

`docs/QUEUE.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. Migration
`backend/app/db/migrations/0016_queue_items.sql` — tabela `queue_items`
(`id`, `payload jsonb`, `status`, `error`, `created_at`, `finished_at`),
índice em `(status, created_at)`. `backend/app/queue/queue_model.py`
(mesmo arquivo da TASK-074) ganhou `save_queue_item(item)` (`INSERT ...
ON CONFLICT DO UPDATE` — cria na primeira chamada, atualiza
`status`/`error`/`finished_at` nas seguintes), `get_queue_item(item_id)`
e `list_queue_items()` (ordem FIFO, `created_at` crescente).

Decisão de design: `FifoQueue`/`QueueItem` (TASK-074) não foram
alterados — continuam puramente em memória. A persistência é mecânica e
explícita: quem processa um item chama `save_queue_item` a cada
transição (`enqueue`/`start`/`complete`/`fail`), mesmo padrão já usado
por `record_usage` (TASK-073) — evita reescrever/acoplar o design já
aprovado da TASK-074 dentro desta TASK. `payload` precisa ser
JSON-serializável para ser persistido (guardado como `jsonb`); nenhuma
validação nova foi adicionada para isso além do erro nativo do driver se
não for.

8 testes de integração novos em
`tests/integration/test_queue_persistence_integration.py`
(save/get/list, atualização por `ON CONFLICT` a cada transição, item
desconhecido, lista vazia, uso conjunto com `FifoQueue` ponta a ponta).
Suíte completa: 597/597 testes aprovados, zero pulados (Ollama local
verificado rodando antes da execução).
