# Observabilidade

Documentação: docs/OBSERVABILITY.md, docs/OPERATIONS.md. TASKs: TASK-005, TASK-006, TASK-078 a TASK-083, TASK-085.

Logging local rotativo e estruturado no PostgreSQL, Execution Trace, métricas básicas.

- `logging_config.py` (TASK-005) — logging local rotativo em arquivo. `configure_logging()`
  configura o logger raiz `claudiao` lendo `CLAUDIAO_LOG_LEVEL`/`CLAUDIAO_LOG_DIR`/
  `CLAUDIAO_LOG_FILE` do ambiente (DEBUG desativado por padrão); `get_logger(nome)`
  retorna um logger filho (`claudiao.<nome>`). Rotação por tamanho (10 MB, 5 backups).
  Lacuna conhecida (TASK-085/TASK-087): o estado "configurado" é uma flag
  de módulo (`_configured`), decidida na primeira chamada de
  `get_logger()` em qualquer lugar do processo — se
  `CLAUDIAO_POSTGRES_*` já estiver no ambiente nesse instante (ex.:
  `config/.env` carregado antes de subir o processo), o handler do
  PostgreSQL é anexado ao logger raiz para o resto da execução; testes
  que dependem de um número fixo de handlers isolam isso explicitamente
  (`tests/unit/test_observability_logging.py`).
- `postgres_log_handler.py` (TASK-006, TASK-083) — `PostgresLogHandler`
  grava cada `LogRecord` na tabela `logs`
  (`backend/app/db/migrations/0002_logs.sql`). `configure_logging()`
  anexa esse handler automaticamente quando `CLAUDIAO_POSTGRES_*` está
  disponível; sem isso, segue só com arquivo. Driver: `psycopg`
  (DEC-006). A montagem de DSN (`build_dsn_from_env()`) foi movida para
  `app.db.connection` na TASK-009, quando um segundo consumidor
  (autenticação) precisou dela — reexportada aqui para compatibilidade.
  `list_recent_logs(limit=50)` (TASK-083) — leitura, mais nova primeiro;
  lacuna conhecida documentada no módulo: nenhum código da aplicação
  chama `logger.error`/`logger.warning` em nenhum ponto real ainda,
  então costuma devolver lista vazia na prática.
- `execution_trace.py` (TASK-078, TASK-079, TASK-082, TASK-083) — `ExecutionTrace`
  (dataclass): registro observável de uma execução (`execution_id`/
  `origin`/`requester`/`objective`/`steps`/`step_durations`/
  `tool_durations`/`errors`/`error_codes`/`usage`/`result`/
  `prompt_version`/`orchestrator_rules_version`), com `step_count`/
  `tools_used`/`duration_seconds` derivados. `add_step(step,
  duration_seconds=None)`/`record_tool_execution(duration_seconds)`/
  `record_error`/`finish` registram o ciclo de vida. Conectado de
  verdade ao `ExecutionOrchestrator` (TASK-079,
  `app.orchestrator.orchestrator`) — ver `backend/app/orchestrator/
  README.md`. Persistência real (TASK-082, `DEC-010`):
  `save_execution_trace`/`get_execution_trace`/`list_execution_traces`
  em `execution_traces` — só o resumo (`step_count`/`tools_used`, não
  `steps`/`errors`/`usage` completos); `ExecutionTraceRecord` é o
  modelo de leitura. `list_failed_execution_traces(limit=50)`
  (TASK-083) — traces com `result IS NULL`, o único sinal de erro com
  dado real hoje.
- `metrics.py` (TASK-080) — funções puras agregando sobre coleções de
  `ExecutionTrace`/`UsageRecord`: `success_rate`,
  `average_duration_seconds`, `average_step_count`, `tool_usage_counts`,
  `failure_counts_by_error_code`, `request_count_by_status`. Cobrem taxa
  de sucesso/tempo médio/número de passos/uso de ferramentas/consumo
  (por status) de `docs/OBSERVABILITY.md`; lacunas conhecidas (uso
  correto/incorreto, falhas por ferramenta/provider, respostas
  bloqueadas por confiança, replanejamentos, erros por provider)
  documentadas no próprio módulo — sem fonte de dado real ainda.
- `health_check.py` (TASK-085) — `run_health_check()`: `modelo/runtime`
  (`OllamaProvider().is_available()`), `postgresql` (`SELECT 1` real),
  `fila` (`list_queue_items()`), `ferramentas/providers principais`
  (`SKIPPED`, nada existe ainda), `configurações críticas`
  (`CLAUDIAO_ACTIVE_MODEL` + chave mestra). `HealthCheckResult.healthy`
  é `False` se qualquer item `FAILED` (`SKIPPED` não conta). Cada
  `FAILED` vira `logger.error`; um resumo vira `INFO`/`WARNING` —
  primeiro código de aplicação a chamar `logger.error`/`warning` de
  verdade (docs/OPERATIONS.md). Chamada no evento de inicialização
  (`app.api.app`, `_lifespan`) e exposta em `GET /health`
  (`app.api.health`).

Testes em `tests/unit/test_observability_logging.py`,
`tests/unit/test_postgres_log_handler.py`,
`tests/unit/test_execution_trace.py` (criação, validação, registro de
etapas/tempos/erros, propriedades derivadas — sem tocar rede/banco),
`tests/unit/test_metrics.py` (cada métrica isolada, sem tocar rede/banco),
`tests/unit/test_health_check.py` (`HealthCheckResult.healthy` isolada),
`tests/integration/test_postgres_log_handler_integration.py` (grava/lê/limpa
de verdade no PostgreSQL local, inclui `list_recent_logs`),
`tests/integration/test_execution_trace_persistence_integration.py`
(`save_execution_trace`/`get_execution_trace`/`list_execution_traces`/
`list_failed_execution_traces` reais) e
`tests/integration/test_health_check_integration.py` (cada checagem
real, com/sem configuração crítica); todos pulam automaticamente se o
banco não estiver disponível.
