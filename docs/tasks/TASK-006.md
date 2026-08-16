# TASK-006 — Criar logging estruturado no PostgreSQL

Status: **Concluída em 2026-08-16**

## Objetivo

Ligar os logs estruturados ao PostgreSQL, depois do logging local rotativo
(TASK-005), conforme a seção "Ponto de partida manual" da especificação mestre
(`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`) e `docs/OBSERVABILITY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fundação" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/OBSERVABILITY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-005 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/OBSERVABILITY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do componente correspondente (config, schema, logging ou catálogo de erros), conforme docs/TESTING.md. Estrutura pura de diretório (sem lógica) não exige teste automatizado.

## Documentação afetada

`docs/OBSERVABILITY.md`, `docs/DATABASE.md`, `docs/tasks/README.md`,
`docs/DECISION_LOG.md` (DEC-006), `backend/app/observability/README.md`,
`backend/app/db/migrations/README.md`

## Encerramento

Concluída em 2026-08-16. Migration `backend/app/db/migrations/0002_logs.sql`
criada e aplicada (tabela `logs`: `timestamp`, `level`, `logger`, `message`,
`context jsonb`, índices em `timestamp`/`level`). Implementado
`backend/app/observability/postgres_log_handler.py` (`PostgresLogHandler`,
`build_dsn_from_env()`, `attach_postgres_handler()`); `configure_logging()`
(TASK-005) passa a anexar esse handler automaticamente quando
`CLAUDIAO_POSTGRES_*` está disponível, sem quebrar o funcionamento só-em-arquivo
quando não está. Primeira dependência externa do backend: `psycopg[binary]`
(DEC-006). Testado manualmente ponta a ponta contra o banco `claudiao` real, e
depois via suíte automatizada: 5 testes unitários (DSN a partir do ambiente,
anexar/não anexar handler, falha de conexão não derruba a aplicação) e 1 teste de
integração real (grava, lê e limpa uma linha na tabela `logs`, pulando
automaticamente se o banco não estiver disponível). 13/13 testes da suíte
aprovados. Retenção cíclica dos logs em banco (seção 35 da especificação) não tem
TASK numerada dedicada — registrada como lacuna conhecida em
`docs/OBSERVABILITY.md`, não implementada aqui.
