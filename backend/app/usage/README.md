# Rastreio de consumo

Documentação: docs/QUOTAS.md, docs/API.md. TASKs: TASK-073, TASK-083.

Registro mínimo de que uma aplicação consumiu uma requisição — base para o sistema de cotas completo (TASK-108 a TASK-114), não implementado aqui.

- `usage_model.py` (TASK-073, TASK-083) — `UsageRecord` (dataclass:
  `id`/`application_id`/`execution_id`/`status`/`created_at`),
  `record_usage(application_id, execution_id, status)` (persistência real
  no PostgreSQL local,
  `backend/app/db/migrations/0015_usage_records.sql`),
  `list_usage_for_application(application_id)` (ordem cronológica).
  `execution_id` é texto, não FK — `Execution` ainda não é persistida em
  tabela própria (fila/observabilidade, TASK-074 em diante).
  `application_id` tem `ON DELETE CASCADE` (excluir a aplicação remove seu
  histórico de consumo). `list_recent_usage_records(limit=50)`
  (TASK-083) — leitura global (qualquer aplicação, não só uma), mais
  recente primeiro; usada pelo painel (`app.panel.routes`, "Consumo").

Chamado por `backend/app/api/executions.py` (`POST /v1/executions`) a
cada desfecho de execução (sucesso, timeout, falha de modelo/ferramenta).
Medir tokens/volume, ciclo de renovação, avisos 80%/95% e bloqueio em
100% são o sistema de cotas completo, TASK-108 a TASK-114 — não
implementados aqui.

Testes em `tests/integration/test_usage_model_integration.py`
(persistência/listagem/ordem cronológica/`ON DELETE CASCADE`/leitura
global reais) e em `tests/integration/test_api_executions_integration.py`
(wiring real: sucesso/falha/timeout geram registro de consumo com o
status certo).
