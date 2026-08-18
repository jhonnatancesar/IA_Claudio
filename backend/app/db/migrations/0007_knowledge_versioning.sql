-- TASK-054 — versionamento de conhecimento (docs/KNOWLEDGE.md, seção 12
-- da especificação mestre): "se um fato confirmado mudar, o sistema
-- mantém a versão anterior, registra a nova versão, marca qual é a
-- atual, preserva... motivo da mudança". Uma mudança de fato é uma nova
-- linha (`knowledge`), nunca um UPDATE de `content` na linha existente.
--
-- `root_id` agrupa todas as versões do mesmo fato (a primeira versão tem
-- `root_id = id`, autoreferência); `version` é sequencial a partir de 1;
-- `is_current` marca a versão vigente — o índice único parcial abaixo
-- garante no banco que só existe uma versão atual por `root_id`;
-- `previous_version_id` encadeia para a versão anterior;
-- `change_reason` guarda o motivo da mudança (preservado, nunca
-- sobrescrito). Preservar fontes é TASK-056, não implementado aqui.
--
-- Aplicado com psql simples (sem ferramenta de migration definida ainda —
-- ver docs/OPEN_QUESTIONS.md, item 1). Idempotente via IF NOT EXISTS.

BEGIN;

ALTER TABLE knowledge ADD COLUMN IF NOT EXISTS root_id uuid;
ALTER TABLE knowledge ADD COLUMN IF NOT EXISTS version integer NOT NULL DEFAULT 1;
ALTER TABLE knowledge ADD COLUMN IF NOT EXISTS is_current boolean NOT NULL DEFAULT true;
ALTER TABLE knowledge ADD COLUMN IF NOT EXISTS previous_version_id uuid REFERENCES knowledge (id);
ALTER TABLE knowledge ADD COLUMN IF NOT EXISTS change_reason text;

UPDATE knowledge SET root_id = id WHERE root_id IS NULL;
ALTER TABLE knowledge ALTER COLUMN root_id SET NOT NULL;

CREATE INDEX IF NOT EXISTS knowledge_root_id_idx ON knowledge (root_id);
CREATE UNIQUE INDEX IF NOT EXISTS knowledge_one_current_per_root_idx
    ON knowledge (root_id) WHERE is_current;

INSERT INTO schema_migrations (version) VALUES ('0007_knowledge_versioning')
ON CONFLICT (version) DO NOTHING;

COMMIT;
