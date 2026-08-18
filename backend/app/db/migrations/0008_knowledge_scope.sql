-- TASK-055 — escopo GLOBAL/APPLICATION:<id> do conhecimento
-- (docs/KNOWLEDGE.md, seção 12 da especificação mestre). `scope_id` só
-- existe quando `scope_type = 'APPLICATION'` (a CHECK abaixo garante essa
-- consistência no próprio banco, defesa em profundidade além da validação
-- em Python).
--
-- Aplicado com psql simples (sem ferramenta de migration definida ainda —
-- ver docs/OPEN_QUESTIONS.md, item 1). Idempotente via IF NOT EXISTS.

BEGIN;

ALTER TABLE knowledge ADD COLUMN IF NOT EXISTS scope_type text
    NOT NULL DEFAULT 'GLOBAL' CHECK (scope_type IN ('GLOBAL', 'APPLICATION'));
ALTER TABLE knowledge ADD COLUMN IF NOT EXISTS scope_id text;

ALTER TABLE knowledge DROP CONSTRAINT IF EXISTS knowledge_scope_id_consistency;
ALTER TABLE knowledge ADD CONSTRAINT knowledge_scope_id_consistency
    CHECK (
        (scope_type = 'GLOBAL' AND scope_id IS NULL)
        OR (scope_type = 'APPLICATION' AND scope_id IS NOT NULL)
    );

CREATE INDEX IF NOT EXISTS knowledge_scope_idx ON knowledge (scope_type, scope_id);

INSERT INTO schema_migrations (version) VALUES ('0008_knowledge_scope')
ON CONFLICT (version) DO NOTHING;

COMMIT;
