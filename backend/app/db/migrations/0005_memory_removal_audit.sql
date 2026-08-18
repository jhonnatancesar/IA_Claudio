-- TASK-051 — auditoria mínima de memória removida (docs/MEMORY.md, seção
-- 11 da especificação mestre): "quando removida, o conteúdo pode
-- desaparecer, mas fica auditoria mínima informando que existiu, quando
-- foi removida e por qual regra". Por isso o conteúdo (`content`) da
-- memória não é copiado para cá, de propósito.
--
-- Aplicado com psql simples (sem ferramenta de migration definida ainda —
-- ver docs/OPEN_QUESTIONS.md, item 1). Idempotente via IF NOT EXISTS.

BEGIN;

CREATE TABLE IF NOT EXISTS memory_removal_audit (
    id          bigserial PRIMARY KEY,
    memory_id   uuid NOT NULL,
    owner_type  text NOT NULL,
    owner_id    text NOT NULL,
    reason      text NOT NULL,
    removed_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS memory_removal_audit_owner_idx
    ON memory_removal_audit (owner_type, owner_id);

INSERT INTO schema_migrations (version) VALUES ('0005_memory_removal_audit')
ON CONFLICT (version) DO NOTHING;

COMMIT;
