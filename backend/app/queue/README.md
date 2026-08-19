# Fila

Documentação: docs/QUEUE.md. TASKs: TASK-074 a TASK-077.

Fila FIFO persistida no PostgreSQL, estados PENDING/RUNNING/COMPLETED/FAILED, retenção/limpeza. Sem retry automático.

- `queue_model.py` (TASK-074) — só a fila em memória, sem banco ainda
  (persistência é TASK-075). `QueueItemStatus`
  (`PENDING`/`RUNNING`/`COMPLETED`/`FAILED`). `QueueItem` (dataclass:
  `item_id`/`payload`/`status`/`error`/`created_at`/`finished_at`) —
  `start()`/`complete()`/`fail(error)` com transições validadas
  (`InvalidQueueItemStateError`), mesmo espírito de `Execution`
  (TASK-020). `FifoQueue` — `enqueue(payload)` (cria um `QueueItem` novo,
  `PENDING`, no fim da fila) e `dequeue()` (tira o mais antigo e já o
  inicia — `PENDING` → `RUNNING` —, `QueueEmptyError` se vazia). Sem
  retry automático: um item `FAILED` não volta à fila. `payload` é
  genérico (`Any`) — a fila não sabe o que está enfileirando.

Testes em `tests/unit/test_queue_model.py` (estados, transições
inválidas, ordem FIFO, fila vazia, ciclo completo).
