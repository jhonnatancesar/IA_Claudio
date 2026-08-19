-- TASK-075 — persistência da fila FIFO (seção 27 da especificação
-- mestre, docs/QUEUE.md). Reflete o estado atual de um QueueItem
-- (TASK-074, backend/app/queue/queue_model.py): `id` (mesmo `item_id` em
-- memória), `payload` (jsonb — o item precisa ser JSON-serializável para
-- ser persistido), `status`, `error`, `created_at`, `finished_at`.
--
-- Aplicado com psql simples. Idempotente via IF NOT EXISTS.

BEGIN;

CREATE TABLE IF NOT EXISTS queue_items (
    id           uuid PRIMARY KEY,
    payload      jsonb NOT NULL,
    status       text NOT NULL DEFAULT 'PENDING',
    error        text,
    created_at   timestamptz NOT NULL DEFAULT now(),
    finished_at  timestamptz
);

CREATE INDEX IF NOT EXISTS idx_queue_items_status_created_at
    ON queue_items (status, created_at);

INSERT INTO schema_migrations (version) VALUES ('0016_queue_items')
ON CONFLICT (version) DO NOTHING;

COMMIT;
