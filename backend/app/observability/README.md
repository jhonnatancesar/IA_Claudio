# Observabilidade

Documentação: docs/OBSERVABILITY.md. TASKs: TASK-005, TASK-006, TASK-078 a TASK-083.

Logging local rotativo e estruturado no PostgreSQL, Execution Trace, métricas básicas.

- `logging_config.py` (TASK-005) — logging local rotativo em arquivo. `configure_logging()`
  configura o logger raiz `claudiao` lendo `CLAUDIAO_LOG_LEVEL`/`CLAUDIAO_LOG_DIR`/
  `CLAUDIAO_LOG_FILE` do ambiente (DEBUG desativado por padrão); `get_logger(nome)`
  retorna um logger filho (`claudiao.<nome>`). Rotação por tamanho (10 MB, 5 backups).
  Sem escrita no PostgreSQL ainda — isso é TASK-006.

Testes em `tests/unit/test_observability_logging.py`.
