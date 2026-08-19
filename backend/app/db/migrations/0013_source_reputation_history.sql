-- TASK-063 — histórico de reputação de fontes (docs/TRUST_GUARDRAILS.md,
-- seção 14/15 da especificação mestre: "O sistema mantém base de
-- reputação de fontes, avaliada dinamicamente e registrada para
-- reutilização futura"). Cada mudança de reputação (`set_source_reputation`,
-- TASK-061) grava uma linha aqui, na mesma transação da mudança — nunca
-- reescrita, só acumulada.
--
-- `ON DELETE CASCADE`: mesmo raciocínio de `knowledge_evidence`
-- (TASK-056) — se a fonte for removida (uso administrativo, nunca pelo
-- código normal), o histórico não deve virar referência órfã nem
-- bloquear a remoção.
--
-- Aplicado com psql simples (sem ferramenta de migration definida ainda —
-- ver docs/OPEN_QUESTIONS.md, item 1). Idempotente via IF NOT EXISTS.

BEGIN;

CREATE TABLE IF NOT EXISTS source_reputation_history (
    id                   bigserial PRIMARY KEY,
    source_id            uuid NOT NULL REFERENCES sources (id) ON DELETE CASCADE,
    previous_reputation  text NOT NULL,
    new_reputation       text NOT NULL,
    changed_at           timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS source_reputation_history_source_id_idx
    ON source_reputation_history (source_id);

INSERT INTO schema_migrations (version) VALUES ('0013_source_reputation_history')
ON CONFLICT (version) DO NOTHING;

COMMIT;
