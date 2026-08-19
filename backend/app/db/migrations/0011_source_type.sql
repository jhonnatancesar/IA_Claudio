-- TASK-060 — tipo de fonte PRIMARY/SECONDARY/UNKNOWN (docs/TRUST_GUARDRAILS.md,
-- seção 14/15 da especificação mestre: "Tipos de fonte: PRIMARY /
-- SECONDARY / UNKNOWN"). `UNKNOWN` por padrão — uma fonte recém-
-- registrada ainda não foi classificada.
--
-- Aplicado com psql simples (sem ferramenta de migration definida ainda —
-- ver docs/OPEN_QUESTIONS.md, item 1). Idempotente via IF NOT EXISTS.

BEGIN;

ALTER TABLE sources ADD COLUMN IF NOT EXISTS source_type text
    NOT NULL DEFAULT 'UNKNOWN' CHECK (source_type IN ('PRIMARY', 'SECONDARY', 'UNKNOWN'));

INSERT INTO schema_migrations (version) VALUES ('0011_source_type')
ON CONFLICT (version) DO NOTHING;

COMMIT;
