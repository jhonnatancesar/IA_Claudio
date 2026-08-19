-- TASK-059 — cadastro de fontes (docs/TRUST_GUARDRAILS.md, seção 14/15
-- da especificação mestre). Só a identidade da fonte por ora: `identifier`
-- (URL/domínio) e `id` (chave usada por TASKs futuras — tipo
-- PRIMARY/SECONDARY/UNKNOWN é TASK-060, reputação é TASK-061 em diante,
-- blacklist é TASK-064 em diante — para referenciar esta linha).
-- `identifier` é único: registrar a mesma fonte duas vezes reaproveita o
-- cadastro existente, não duplica.
--
-- Aplicado com psql simples (sem ferramenta de migration definida ainda —
-- ver docs/OPEN_QUESTIONS.md, item 1). Idempotente via IF NOT EXISTS.

BEGIN;

CREATE TABLE IF NOT EXISTS sources (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    identifier  text NOT NULL UNIQUE,
    created_at  timestamptz NOT NULL DEFAULT now()
);

INSERT INTO schema_migrations (version) VALUES ('0010_sources')
ON CONFLICT (version) DO NOTHING;

COMMIT;
