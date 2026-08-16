# Persistência (PostgreSQL)

Documentação: docs/DATABASE.md. TASKs: TASK-003, TASK-004, TASK-009.

Configuração de acesso ao PostgreSQL local e schema inicial. Demais domínios de dados ganham schema nas TASKs dos respectivos blocos funcionais.

- `connection.py` (TASK-009, extraído de `app.observability.postgres_log_handler`
  onde nasceu na TASK-006) — `build_dsn_from_env()` (monta a DSN a partir de
  `CLAUDIAO_POSTGRES_*`, retorna `None` se incompleta) e `connect()` (abre uma
  conexão nova, levanta `RuntimeError` se a configuração estiver ausente). Ponto
  único de acesso ao banco para os demais módulos.
- `migrations/` — ver README próprio.
