# TASK-009 — Criar autenticação de usuários

Status: **Concluída em 2026-08-16**

## Objetivo

Criar autenticação de usuários, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Segurança e identidade") e `docs/AUTHENTICATION.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Segurança e identidade" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/AUTHENTICATION.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-008 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/AUTHENTICATION.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de autenticação/autorização (criação de usuário, papéis, validação de API key, criptografia/descriptografia de segredo), conforme docs/TESTING.md.

## Documentação afetada

`docs/AUTHENTICATION.md`, `docs/tasks/README.md`, `backend/app/auth/README.md`,
`backend/app/db/README.md`, `backend/app/observability/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/auth/password.py`
(`hash_password()`/`verify_password()`, PBKDF2-HMAC-SHA256 via `hashlib`, sem
dependência nova, 600.000 iterações, salt aleatório) e `backend/app/auth/users.py`
(`create_user()`/`authenticate_user()` contra a tabela `users` da TASK-004;
`role` só como valor armazenado, autorização por papel fica para TASK-010).

Refactor colateral: a montagem de DSN do PostgreSQL (`build_dsn_from_env`), que
só existia em `app.observability.postgres_log_handler` por ter sido o primeiro
consumidor (TASK-006), foi movida para `backend/app/db/connection.py`
(`build_dsn_from_env()` + `connect()`) para não duplicar quando a autenticação
também precisou dela — sem mudança de comportamento, reexportada no módulo
antigo para compatibilidade. Extraída também a fixture de teste de integração
com o banco (`postgres_dsn`) para `tests/integration/conftest.py`, reaproveitada
pelo teste da TASK-006 e pelo novo da TASK-009.

8 testes unitários novos (`tests/unit/test_password.py`) e 6 de integração real
contra o PostgreSQL local (`tests/integration/test_users_integration.py`:
criação com hash, papel inválido, username duplicado, autenticação correta/
incorreta/usuário inexistente). Suíte completa: 52/52 testes aprovados.
