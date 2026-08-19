-- TASK-073 — rastreio de consumo por aplicação (seção 28 da especificação
-- mestre, docs/QUOTAS.md). Só o registro mínimo de que uma aplicação
-- consumiu uma requisição: quem (application_id), qual execução
-- (execution_id — texto, não FK: Execution ainda não é persistida em
-- tabela própria, isso é a fila/observabilidade, TASK-074 em diante),
-- quando e com que status final. Medição de tokens/volume, ciclos de
-- renovação, avisos 80/95% e bloqueio em 100% são o sistema de cotas
-- completo, TASK-108 a TASK-114 — não implementados aqui.
--
-- Aplicado com psql simples (sem ferramenta de migration definida ainda —
-- ver docs/OPEN_QUESTIONS.md, item 1). Idempotente via IF NOT EXISTS.

BEGIN;

CREATE TABLE IF NOT EXISTS usage_records (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id  uuid NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    execution_id    text NOT NULL,
    status          text NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_usage_records_application_id
    ON usage_records (application_id);

INSERT INTO schema_migrations (version) VALUES ('0015_usage_records')
ON CONFLICT (version) DO NOTHING;

COMMIT;
