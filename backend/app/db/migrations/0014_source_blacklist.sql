-- TASK-064 — blacklist de fontes (docs/TRUST_GUARDRAILS.md, seção 14/15
-- da especificação mestre, "Fontes bloqueadas (blacklist)"): "todo
-- bloqueio guarda origem, motivo, data e responsável".
--
-- `sources.is_blocked` é o estado atual (consulta rápida);
-- `source_blacklist_entries` é o histórico completo de bloqueios e
-- desbloqueios, nunca reescrito — mesmo princípio de
-- `source_reputation_history` (TASK-063). `origin` distingue quem
-- iniciou a ação (`AGENT`/`ADMIN`); `responsible` é a identidade
-- específica (ex.: usuário ADMIN), nula quando `origin = 'AGENT'`.
--
-- Bloqueio automático (TASK-065) e a regra de que só ADMIN pode
-- desbloquear (TASK-066) não são desta migration — só o schema para
-- bloquear/desbloquear mecanicamente, com auditoria.
--
-- Aplicado com psql simples (sem ferramenta de migration definida ainda —
-- ver docs/OPEN_QUESTIONS.md, item 1). Idempotente via IF NOT EXISTS.

BEGIN;

ALTER TABLE sources ADD COLUMN IF NOT EXISTS is_blocked boolean NOT NULL DEFAULT false;

CREATE TABLE IF NOT EXISTS source_blacklist_entries (
    id           bigserial PRIMARY KEY,
    source_id    uuid NOT NULL REFERENCES sources (id) ON DELETE CASCADE,
    action       text NOT NULL CHECK (action IN ('BLOCK', 'UNBLOCK')),
    origin       text NOT NULL CHECK (origin IN ('AGENT', 'ADMIN')),
    responsible  text,
    reason       text NOT NULL,
    created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS source_blacklist_entries_source_id_idx
    ON source_blacklist_entries (source_id);

INSERT INTO schema_migrations (version) VALUES ('0014_source_blacklist')
ON CONFLICT (version) DO NOTHING;

COMMIT;
