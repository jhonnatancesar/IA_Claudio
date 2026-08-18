-- TASK-048 — colunas de rastreamento de uso da memória (docs/MEMORY.md,
-- seção 11 da especificação mestre): frequência (use_count) e last used
-- (last_used_at), base para relevância. Usadas pela política de retenção
-- (TASK-049), não implementada aqui.
--
-- Aplicado com psql simples (sem ferramenta de migration definida ainda —
-- ver docs/OPEN_QUESTIONS.md, item 1). Idempotente via IF NOT EXISTS.

BEGIN;

ALTER TABLE memories ADD COLUMN IF NOT EXISTS use_count integer NOT NULL DEFAULT 0;
ALTER TABLE memories ADD COLUMN IF NOT EXISTS last_used_at timestamptz;

INSERT INTO schema_migrations (version) VALUES ('0004_memory_usage')
ON CONFLICT (version) DO NOTHING;

COMMIT;
