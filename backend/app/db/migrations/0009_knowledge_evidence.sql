-- TASK-056 — evidências e confiança/volatilidade do conhecimento
-- (docs/KNOWLEDGE.md, seção 12 da especificação mestre): "conhecimento
-- provisório/confirmado se apoia em evidências e fontes... e carrega os
-- mesmos níveis de confiança (LOW/MEDIUM/HIGH) e a marca de volatilidade
-- quando aplicável".
--
-- `confidence`/`volatility` reaproveitam o mesmo vocabulário já usado no
-- protocolo (TASK-016) e nos guardrails (TASK-032) — não são um novo
-- enum, só colunas com os mesmos valores permitidos. Nulos são válidos:
-- um fato `RAW` recém-capturado pode não ter confiança/volatilidade
-- avaliadas ainda.
--
-- `knowledge_evidence` guarda evidências como texto livre por ora — o
-- cadastro real de fontes, com reputação e tipo PRIMARY/SECONDARY/UNKNOWN,
-- é TASK-059 em diante; vincular evidências a uma fonte cadastrada de
-- verdade fica para quando esse sistema existir.
--
-- Aplicado com psql simples (sem ferramenta de migration definida ainda —
-- ver docs/OPEN_QUESTIONS.md, item 1). Idempotente via IF NOT EXISTS.

BEGIN;

ALTER TABLE knowledge ADD COLUMN IF NOT EXISTS confidence text
    CHECK (confidence IN ('LOW', 'MEDIUM', 'HIGH'));
ALTER TABLE knowledge ADD COLUMN IF NOT EXISTS volatility text
    CHECK (volatility IN ('VOLATILE', 'NON_VOLATILE'));

-- ON DELETE CASCADE: conhecimento nunca é apagado automaticamente pelo
-- código (TASK-052), mas testes e uso administrativo direto no banco
-- podem remover uma linha; a evidência associada não deve virar
-- referência órfã nem bloquear a remoção.
CREATE TABLE IF NOT EXISTS knowledge_evidence (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_id uuid NOT NULL REFERENCES knowledge (id) ON DELETE CASCADE,
    description  text NOT NULL,
    created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS knowledge_evidence_knowledge_id_idx
    ON knowledge_evidence (knowledge_id);

INSERT INTO schema_migrations (version) VALUES ('0009_knowledge_evidence')
ON CONFLICT (version) DO NOTHING;

COMMIT;
