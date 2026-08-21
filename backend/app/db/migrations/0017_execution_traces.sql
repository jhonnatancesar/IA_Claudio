-- TASK-082 — persistência do Execution Trace (DEC-010, docs/DECISION_LOG.md).
-- A especificação mestre não exige isso explicitamente para o Execution
-- Trace (diferente da fila, seção 27) — decisão tomada nesta TASK, com
-- confirmação explícita do usuário, para o painel poder mostrar
-- execuções passadas (docs/PANEL.md).
--
-- Reflete os campos de ExecutionTrace (TASK-078/079,
-- backend/app/observability/execution_trace.py) úteis para exibição no
-- painel: não guarda `steps` completos (cada ModelStep, com parâmetros
-- arbitrários) nem `step_durations`/`tool_durations` individualmente —
-- só o resumo (step_count, tools_used como lista de nomes). Guardar o
-- detalhe completo de cada etapa é escopo de uma TASK futura, se um
-- dia for pedido.
--
-- Aplicado com psql simples. Idempotente via IF NOT EXISTS.

BEGIN;

CREATE TABLE IF NOT EXISTS execution_traces (
    execution_id    uuid PRIMARY KEY,
    origin          text NOT NULL,
    requester       text NOT NULL,
    objective       text NOT NULL,
    started_at      timestamptz NOT NULL,
    finished_at     timestamptz,
    result          text,
    step_count      integer NOT NULL,
    tools_used      jsonb NOT NULL DEFAULT '[]'::jsonb,
    prompt_version  text NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_execution_traces_started_at
    ON execution_traces (started_at DESC);

INSERT INTO schema_migrations (version) VALUES ('0017_execution_traces')
ON CONFLICT (version) DO NOTHING;

COMMIT;
