-- TASK-044 — schema da memória persistente (docs/MEMORY.md, seção 11 da
-- especificação mestre). Escopos mínimos USER/APPLICATION já como colunas
-- (owner_type/owner_id) — a separação de fato (garantir que uma consulta só
-- devolve memórias do próprio dono) é lógica de aplicação, TASK-045, não
-- deste schema. Relevância/frequência/last_used (TASK-048) e auditoria de
-- remoção (TASK-051) ganham colunas/tabela própria nas TASKs correspondentes.
--
-- Aplicado com psql simples (sem ferramenta de migration definida ainda — ver
-- docs/OPEN_QUESTIONS.md, item 1). Idempotente via IF NOT EXISTS.

BEGIN;

CREATE TABLE IF NOT EXISTS memories (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_type  text NOT NULL CHECK (owner_type IN ('USER', 'APPLICATION')),
    owner_id    text NOT NULL,
    content     text NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS memories_owner_idx ON memories (owner_type, owner_id);

INSERT INTO schema_migrations (version) VALUES ('0003_memory')
ON CONFLICT (version) DO NOTHING;

COMMIT;
