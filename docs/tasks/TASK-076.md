# TASK-076 — Criar estados da fila

Status: **Concluída em 2026-08-21**

## Objetivo

Criar estados da fila, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Fila") e `docs/QUEUE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fila" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/QUEUE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-075 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/QUEUE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários e de integração da fila (estados, persistência, retenção), conforme docs/TESTING.md.

## Documentação afetada

`docs/QUEUE.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-21. `backend/app/queue/queue_model.py` (mesmo
arquivo das TASK-074/075) ganhou `start_queue_item(item_id)`/
`complete_queue_item(item_id)`/`fail_queue_item(item_id, error)`:
transições de estado aplicadas direto a um item já persistido, a partir
só do `item_id` — cobrem o caso em que quem processa a fila não tem mais
o objeto `QueueItem` original em memória (carregado de novo via
`get_queue_item`/`list_queue_items`, outro processo, outra requisição).
Cada função carrega o item do banco, reaplica a mesma validação de
transição de `QueueItem.start`/`complete`/`fail` (TASK-074, reaproveitada
sem duplicar regra) e grava com `save_queue_item` (TASK-075).
`QueueItemNotFoundError` (novo) se `item_id` não existir.
`list_queue_items_by_status(status)` completa o conjunto, filtrando a
listagem por estado.

Decisão de design: não foi adicionado um "dequeue" que busca e inicia o
próximo item `PENDING` direto do banco (ex.: via `FOR UPDATE SKIP
LOCKED`) — isso é concorrência/coordenação entre workers, uma decisão de
arquitetura maior que "criar estados da fila" não pede explicitamente;
fica em aberto para quando (se) uma TASK futura precisar de verdade de
múltiplos processos consumindo a mesma fila.

13 testes de integração novos em
`tests/integration/test_queue_states_integration.py` (cada transição via
`item_id`, item desconhecido, transição inválida, sem retry, filtro por
status, ciclo completo). Suíte completa: 610/610 testes aprovados, zero
pulados (Ollama precisou ser iniciado manualmente antes da suíte — não
estava rodando no início desta TASK).
