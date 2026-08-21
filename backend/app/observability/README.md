# Observabilidade

Documentação: docs/OBSERVABILITY.md. TASKs: TASK-005, TASK-006, TASK-078 a TASK-083.

Logging local rotativo e estruturado no PostgreSQL, Execution Trace, métricas básicas.

- `logging_config.py` (TASK-005) — logging local rotativo em arquivo. `configure_logging()`
  configura o logger raiz `claudiao` lendo `CLAUDIAO_LOG_LEVEL`/`CLAUDIAO_LOG_DIR`/
  `CLAUDIAO_LOG_FILE` do ambiente (DEBUG desativado por padrão); `get_logger(nome)`
  retorna um logger filho (`claudiao.<nome>`). Rotação por tamanho (10 MB, 5 backups).
- `postgres_log_handler.py` (TASK-006) — `PostgresLogHandler` grava cada
  `LogRecord` na tabela `logs` (`backend/app/db/migrations/0002_logs.sql`).
  `configure_logging()` anexa esse handler automaticamente quando
  `CLAUDIAO_POSTGRES_*` está disponível; sem isso, segue só com arquivo. Driver:
  `psycopg` (DEC-006). A montagem de DSN (`build_dsn_from_env()`) foi movida
  para `app.db.connection` na TASK-009, quando um segundo consumidor
  (autenticação) precisou dela — reexportada aqui para compatibilidade.
- `execution_trace.py` (TASK-078, TASK-079) — `ExecutionTrace` (dataclass):
  registro observável de uma execução (`execution_id`/`origin`/`requester`/
  `objective`/`steps`/`step_durations`/`tool_durations`/`errors`/
  `error_codes`/`usage`/`result`/`prompt_version`/
  `orchestrator_rules_version`), com `step_count`/`tools_used`/
  `duration_seconds` derivados. `add_step(step, duration_seconds=None)`/
  `record_tool_execution(duration_seconds)`/`record_error`/`finish`
  registram o ciclo de vida. Conectado de verdade ao
  `ExecutionOrchestrator` (TASK-079, `app.orchestrator.orchestrator`) —
  ver `backend/app/orchestrator/README.md`. Ainda não persistido.

Testes em `tests/unit/test_observability_logging.py`,
`tests/unit/test_postgres_log_handler.py`,
`tests/unit/test_execution_trace.py` (criação, validação, registro de
etapas/tempos/erros, propriedades derivadas — sem tocar rede/banco) e
`tests/integration/test_postgres_log_handler_integration.py` (grava/lê/limpa de
verdade no PostgreSQL local; pula automaticamente se o banco não estiver
disponível).
