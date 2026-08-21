# Fila

Documentação: docs/QUEUE.md. TASKs: TASK-074 a TASK-077.

Fila FIFO persistida no PostgreSQL, estados PENDING/RUNNING/COMPLETED/FAILED, retenção/limpeza. Sem retry automático.

- `queue_model.py` (TASK-074 a TASK-076) — `QueueItemStatus`
  (`PENDING`/`RUNNING`/`COMPLETED`/`FAILED`). `QueueItem` (dataclass:
  `item_id`/`payload`/`status`/`error`/`created_at`/`finished_at`) —
  `start()`/`complete()`/`fail(error)` com transições validadas
  (`InvalidQueueItemStateError`), mesmo espírito de `Execution`
  (TASK-020). `FifoQueue` — `enqueue(payload)` (cria um `QueueItem` novo,
  `PENDING`, no fim da fila) e `dequeue()` (tira o mais antigo e já o
  inicia — `PENDING` → `RUNNING` —, `QueueEmptyError` se vazia); ambos
  puramente em memória, sem tocar o banco sozinhos. Sem retry
  automático: um item `FAILED` não volta à fila. `payload` é genérico
  (`Any`) — a fila não sabe o que está enfileirando (precisa ser
  JSON-serializável para ser persistido).
  Persistência real (TASK-075): `save_queue_item(item)` (`INSERT ...
  ON CONFLICT DO UPDATE` em `queue_items`,
  `backend/app/db/migrations/0016_queue_items.sql`, `payload` como
  `jsonb`) — mecânico e explícito, chamado por quem processa o item a
  cada transição, mesmo padrão de `app.usage.usage_model.record_usage`
  (TASK-073); `get_queue_item(item_id)`; `list_queue_items()` (ordem
  FIFO, `created_at` crescente).
  Estados aplicados a um item já persistido (TASK-076):
  `start_queue_item(item_id)`/`complete_queue_item(item_id)`/
  `fail_queue_item(item_id, error)` — carregam o item pelo `item_id`
  (sem precisar do objeto `QueueItem` original em memória), reaplicam a
  mesma validação de `QueueItem.start`/`complete`/`fail` e gravam com
  `save_queue_item`; `QueueItemNotFoundError` se `item_id` não existir.
  `list_queue_items_by_status(status)` filtra a listagem por estado.

Testes em `tests/unit/test_queue_model.py` (estados, transições
inválidas, ordem FIFO, fila vazia, ciclo completo, sem tocar o banco),
`tests/integration/test_queue_persistence_integration.py` (persistência
real: save/get/list, atualização por `ON CONFLICT`, uso em conjunto com
`FifoQueue`) e `tests/integration/test_queue_states_integration.py`
(transições por `item_id` direto no banco, filtro por status, item
desconhecido).
