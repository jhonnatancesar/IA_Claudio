-- TASK-061 — reputação de fonte LOW/MEDIUM/HIGH (docs/TRUST_GUARDRAILS.md,
-- seção 14/15 da especificação mestre: "Confiabilidade: LOW / MEDIUM /
-- HIGH"). `MEDIUM` por padrão — uma fonte recém-registrada ainda não tem
-- histórico que justifique confiança alta nem baixa; `MEDIUM` já implica
-- aviso ao ser usada (seção 15: "Fonte MEDIUM sempre gera aviso"), o que é
-- o comportamento conservador correto para algo ainda não avaliado.
--
-- Aplicado com psql simples (sem ferramenta de migration definida ainda —
-- ver docs/OPEN_QUESTIONS.md, item 1). Idempotente via IF NOT EXISTS.

BEGIN;

ALTER TABLE sources ADD COLUMN IF NOT EXISTS reputation text
    NOT NULL DEFAULT 'MEDIUM' CHECK (reputation IN ('LOW', 'MEDIUM', 'HIGH'));

INSERT INTO schema_migrations (version) VALUES ('0012_source_reputation')
ON CONFLICT (version) DO NOTHING;

COMMIT;
