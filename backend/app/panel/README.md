# Painel

Documentação: docs/PANEL.md. TASKs: TASK-081 a TASK-083, TASK-115 a TASK-122.

Painel web read-only (fila, execução atual, status, logs, erros, consumo) e, depois, painel administrativo completo (usuários, API keys, providers, cotas, configurações, manutenção, backups, atualizações, blacklist).

- `routes.py` (TASK-081 a TASK-083) — `GET /panel` (FastAPI, incluído em
  `app.api.app`): página HTML somente leitura com cinco seções — Fila
  (`app.queue.queue_model.list_queue_items`) — `item_id`/`status`/
  `created_at`/`finished_at`, nunca `payload`; Execuções
  (`app.observability.execution_trace.list_execution_traces`,
  TASK-082, `DEC-010`) — `execution_id`/`requester`/`objective`/status
  (derivado de `succeeded`)/`result`/`duration_seconds`; Erros
  (`list_failed_execution_traces`, TASK-083 — traces com `result IS
  NULL`); Logs recentes
  (`app.observability.postgres_log_handler.list_recent_logs`,
  TASK-083); Consumo (`app.usage.usage_model.
  list_recent_usage_records`, TASK-083). `objective`/`result`/mensagens
  de log são texto livre — escapados via `html.escape` antes de entrar
  na página. `render_panel_page(items, traces, logs, failed_traces,
  usage_records)` monta o HTML, separado da rota para ser testável sem
  FastAPI. Sem autenticação (regras de acesso do `docs/PANEL.md` valem
  para o painel administrativo completo, TASK-115+, não para este). Com
  a TASK-083, o bloco "Observabilidade inicial" (TASK-078 a TASK-083)
  está completo.

Testes em `tests/unit/test_panel_routes.py` (`render_panel_page`
isolada — cada seção vazia/com dado, `payload` nunca aparece,
`objective`/`result`/mensagens de log escapados contra HTML) e
`tests/integration/test_panel_integration.py` (`GET /panel` real via
`TestClient`, com item de fila, trace de execução (sucesso e falha),
log e registro de consumo persistidos de verdade no PostgreSQL local;
pula automaticamente se o banco não estiver disponível).
