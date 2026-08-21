# Painel

Documentação: docs/PANEL.md. TASKs: TASK-081 a TASK-083, TASK-115 a TASK-122.

Painel web read-only (fila, execução atual, status, logs, erros, consumo) e, depois, painel administrativo completo (usuários, API keys, providers, cotas, configurações, manutenção, backups, atualizações, blacklist).

- `routes.py` (TASK-081) — `GET /panel` (FastAPI, incluído em
  `app.api.app`): página HTML somente leitura mostrando a fila atual
  (`app.queue.queue_model.list_queue_items`) — `item_id`/`status`/
  `created_at`/`finished_at`, nunca `payload`. `render_panel_page(items)`
  monta o HTML, separado da rota para ser testável sem FastAPI. Sem
  autenticação (regras de acesso do `docs/PANEL.md` valem para o painel
  administrativo completo, TASK-115+, não para este). Execuções/erros/
  logs/consumo são TASK-082/083.

Testes em `tests/unit/test_panel_routes.py` (`render_panel_page`
isolada — fila vazia, campos, `payload` nunca aparece) e
`tests/integration/test_panel_integration.py` (`GET /panel` real via
`TestClient`, com item persistido de verdade no PostgreSQL local; pula
automaticamente se o banco não estiver disponível).
