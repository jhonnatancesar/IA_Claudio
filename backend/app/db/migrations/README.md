# Migrations

Documentação: docs/DATABASE.md. TASKs: TASK-004.

Migrations do schema do PostgreSQL, aplicadas como SQL puro via `psql`
(`-f arquivo.sql`), sem ferramenta de migration dedicada — essa escolha ainda não foi
feita (ver docs/OPEN_QUESTIONS.md, item 1). Numeração sequencial nos arquivos
(`0001_...`, `0002_...`); cada migration é registrada em `schema_migrations` ao ser
aplicada.

- `0001_initial_schema.sql` (TASK-004) — schema mínimo: `users`, `applications`,
  `settings`, `schema_migrations`.
- `0002_logs.sql` (TASK-006) — tabela `logs` para o logging estruturado
  (docs/OBSERVABILITY.md).

Quando a stack de implementação for escolhida, uma ferramenta de migration própria
dela pode substituir esse mecanismo manual — decisão futura, registrada em
`docs/DECISION_LOG.md` quando acontecer.
