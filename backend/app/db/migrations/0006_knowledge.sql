-- TASK-052 — schema do modelo de conhecimento RAW/PROVISIONAL/CONFIRMED
-- (docs/KNOWLEDGE.md, seção 12 da especificação mestre). Diferente de
-- `memories` (TASK-044), conhecimento nunca é apagado automaticamente —
-- por isso não há coluna equivalente a auditoria de remoção aqui.
--
-- Só os campos que esta TASK precisa: identidade, status e conteúdo.
-- Versionamento (TASK-054), escopo GLOBAL/APPLICATION (TASK-055) e
-- evidências/fontes (TASK-056) ganham colunas/tabelas próprias nas TASKs
-- correspondentes.
--
-- Aplicado com psql simples (sem ferramenta de migration definida ainda —
-- ver docs/OPEN_QUESTIONS.md, item 1). Idempotente via IF NOT EXISTS.

BEGIN;

CREATE TABLE IF NOT EXISTS knowledge (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    status      text NOT NULL DEFAULT 'RAW'
                CHECK (status IN ('RAW', 'PROVISIONAL', 'CONFIRMED')),
    content     text NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);

INSERT INTO schema_migrations (version) VALUES ('0006_knowledge')
ON CONFLICT (version) DO NOTHING;

COMMIT;
