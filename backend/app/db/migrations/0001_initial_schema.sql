-- TASK-004 — schema inicial do banco Claudião.
-- Cobre somente usuários, aplicações, configurações e o registro básico de
-- migrations aplicadas (docs/tasks/TASK-004.md). Os demais domínios de dados
-- (memória, conhecimento, fontes, fila, execuções, logs, auditoria, cotas,
-- atualizações, backups — ver docs/DATABASE.md) ganham schema próprio nas TASKs
-- dos respectivos blocos funcionais.
--
-- Aplicado com psql simples (sem ferramenta de migration definida ainda — ver
-- docs/OPEN_QUESTIONS.md, item 1). Idempotente via IF NOT EXISTS para poder ser
-- reaplicado sem erro.

BEGIN;

-- Registro básico de migrations aplicadas.
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     text PRIMARY KEY,
    applied_at  timestamptz NOT NULL DEFAULT now()
);

-- Usuários humanos (docs/AUTHENTICATION.md). Perfis ADMIN e USER (seção 31 da
-- especificação mestre). Hash de senha, não a senha em texto plano.
CREATE TABLE IF NOT EXISTS users (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    username      text NOT NULL UNIQUE,
    password_hash text NOT NULL,
    role          text NOT NULL CHECK (role IN ('ADMIN', 'USER')),
    created_at    timestamptz NOT NULL DEFAULT now(),
    updated_at    timestamptz NOT NULL DEFAULT now()
);

-- Aplicações externas (docs/API.md, docs/AUTHENTICATION.md). Cada aplicação tem
-- sua própria API key; aqui só o hash é armazenado.
CREATE TABLE IF NOT EXISTS applications (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name          text NOT NULL UNIQUE,
    api_key_hash  text NOT NULL UNIQUE,
    created_at    timestamptz NOT NULL DEFAULT now(),
    updated_at    timestamptz NOT NULL DEFAULT now()
);

-- Configurações administráveis em runtime pelo painel (docs/PANEL.md), distintas
-- do arquivo de configuração central de bootstrap (docs/ARCHITECTURE.md,
-- config/.env* — TASK-002). Ex.: modelo ativo, limiares de cota.
CREATE TABLE IF NOT EXISTS settings (
    key         text PRIMARY KEY,
    value       jsonb NOT NULL,
    updated_at  timestamptz NOT NULL DEFAULT now()
);

INSERT INTO schema_migrations (version) VALUES ('0001_initial_schema')
ON CONFLICT (version) DO NOTHING;

COMMIT;
