# TASK-004 — Criar schema inicial do banco

Status: **Concluída em 2026-08-16**

## Objetivo

Criar somente o schema inicial necessário para sustentar usuários, aplicações,
configurações e registros básicos, conforme a seção "Ponto de partida manual" da
especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`) e
`docs/DATABASE.md`.

## Escopo

Schema mínimo (usuários, aplicações, configurações, registros básicos) apenas — os
demais domínios de dados listados em `docs/DATABASE.md` (memória, conhecimento,
fontes, fila, execuções etc.) ganham schema próprio nas TASKs dos respectivos blocos
funcionais, não nesta TASK. Nenhuma funcionalidade de TASK posterior deve ser
adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-003 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/DATABASE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do componente correspondente (config, schema, logging ou catálogo de erros), conforme docs/TESTING.md. Estrutura pura de diretório (sem lógica) não exige teste automatizado.

## Documentação afetada

`docs/DATABASE.md`, `docs/tasks/README.md`, `backend/app/db/migrations/README.md`

## Encerramento

Concluída em 2026-08-16: `backend/app/db/migrations/0001_initial_schema.sql` criado
e aplicado no banco `claudiao` (via `psql`, com o role `claudiao_app`) — 4 tabelas:
`schema_migrations` (registro básico de migrations), `users` (usuários, com
`role` ADMIN/USER), `applications` (aplicações externas, hash de API key) e
`settings` (configurações administráveis em runtime). Verificado com `\dt` e
consulta a `schema_migrations`. Nenhum schema de memória, conhecimento, fontes,
fila, execuções, logs, auditoria, cotas, atualizações ou backups foi criado — fica
para as TASKs dos respectivos blocos funcionais. Nenhuma ferramenta de migration
foi escolhida; a aplicação é manual via SQL puro (`docs/OPEN_QUESTIONS.md`, item 1).
