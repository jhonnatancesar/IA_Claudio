# TASK-010 — Criar roles ADMIN e USER

Status: **Concluída em 2026-08-16**

## Objetivo

Criar roles ADMIN e USER, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Segurança e identidade") e `docs/AUTHENTICATION.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Segurança e identidade" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/AUTHENTICATION.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-009 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/AUTHENTICATION.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de autenticação/autorização (criação de usuário, papéis, validação de API key, criptografia/descriptografia de segredo), conforme docs/TESTING.md.

## Documentação afetada

`docs/AUTHENTICATION.md`, `docs/ERROR_CATALOG.md`, `docs/tasks/README.md`,
`backend/app/auth/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/auth/roles.py`: `Role`
(`ADMIN`/`USER`), `is_admin(role)`, `require_admin(role, details=None)`
(levanta `ClaudiaoError` com o novo código `2001`/403,
`FORBIDDEN_ADMIN_ONLY`, registrado no catálogo da TASK-007). Opera sobre a
string `role` em vez da classe `User` para não criar import circular com
`app.auth.users`. Pequeno refactor colateral: `VALID_ROLES` em `users.py`
passou a derivar de `Role` em vez de uma tupla hardcoded duplicada — mesmo
comportamento externo (`InvalidRoleError` continua igual). Ainda sem nenhum
chamador real (painel administrativo é TASK-115 em diante) — só a primitiva de
autorização. 8 testes unitários novos em `tests/unit/test_roles.py`. Suíte
completa: 60/60 testes aprovados.
