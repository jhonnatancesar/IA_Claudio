# Fila

Fonte: seção 27 da especificação mestre.

A V1 tem fila **FIFO** persistida no PostgreSQL.

## Estados

`PENDING / RUNNING / COMPLETED / FAILED`.

## Retenção e falhas

- Registros antigos são removidos conforme política de retenção.
- Em caso de falha, o item é registrado e o processamento segue para a próxima
  tarefa — **sem retry automático**. Retomada de execução interrompida fica fora da
  V1 (ver `OUT_OF_SCOPE.md`).

## Relação com manutenção

Ao entrar em modo de manutenção, todas as tarefas pendentes da fila são descartadas
(ver `OPERATIONS.md`).

## TASKs relacionadas

TASK-074 a TASK-077: criar fila FIFO, persistir no PostgreSQL, estados da fila,
retenção/limpeza.

**Implementação (TASK-074):** `backend/app/queue/queue_model.py` — só a
fila em memória, no mesmo espírito do modelo de `Execution` (TASK-020):
`QueueItemStatus` (`PENDING`/`RUNNING`/`COMPLETED`/`FAILED`, o conjunto
acima), `QueueItem` (dataclass com transições validadas —
`start()`/`complete()`/`fail(error)`, `InvalidQueueItemStateError` para
transição inválida) e `FifoQueue` (`enqueue(payload)`/`dequeue()` em
ordem de chegada, `QueueEmptyError` ao tirar de uma fila vazia).
`dequeue()` já inicia o item (`PENDING` → `RUNNING`) antes de devolvê-lo.
Sem retry automático: `fail()` não permite nova transição depois —
testado explicitamente. Persistência no PostgreSQL (TASK-075), estados
adicionais e retenção/limpeza (TASK-076/077) não são desta TASK; nenhuma
TASK conecta esta fila a `POST /v1/executions`, que continua síncrono
ponta a ponta (TASK-069).

**Implementação (TASK-075):** `save_queue_item(item)`/`get_queue_item
(item_id)`/`list_queue_items()` (mesmo módulo,
`backend/app/queue/queue_model.py`) — persistência real em `queue_items`
(`backend/app/db/migrations/0016_queue_items.sql`, `payload` como
`jsonb`). `save_queue_item` é `INSERT ... ON CONFLICT DO UPDATE`:
primeira chamada cria a linha (`PENDING`), chamadas seguintes atualizam
`status`/`error`/`finished_at`. Mecânico e explícito — `FifoQueue.
enqueue`/`dequeue` (TASK-074) continuam puramente em memória, sem tocar
o banco sozinhas; quem processa a fila chama `save_queue_item` a cada
transição, mesmo padrão de `record_usage` (TASK-073). `list_queue_items`
devolve em ordem FIFO (`created_at` crescente). Estados adicionais
(TASK-076) e retenção/limpeza (TASK-077) não são desta TASK.
