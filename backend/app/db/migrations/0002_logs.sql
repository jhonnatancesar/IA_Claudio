-- TASK-006 — logging estruturado no PostgreSQL (docs/OBSERVABILITY.md).
-- Tabela genérica de linhas de log; não é o Execution Trace (isso é TASK-078).
-- Retenção cíclica descrita na especificação (seção 35) ainda não tem
-- implementação — sem TASK numerada dedicada a isso no backlog; fica registrada
-- como lacuna em docs/OBSERVABILITY.md até haver uma TASK que a cubra.

BEGIN;

CREATE TABLE IF NOT EXISTS logs (
    id          bigserial PRIMARY KEY,
    "timestamp" timestamptz NOT NULL DEFAULT now(),
    level       text NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR')),
    logger      text NOT NULL,
    message     text NOT NULL,
    context     jsonb
);

CREATE INDEX IF NOT EXISTS logs_timestamp_idx ON logs ("timestamp");
CREATE INDEX IF NOT EXISTS logs_level_idx ON logs (level);

INSERT INTO schema_migrations (version) VALUES ('0002_logs')
ON CONFLICT (version) DO NOTHING;

COMMIT;
