# TASK-011 — Criar autenticação de aplicações via API key

Status: **Concluída em 2026-08-16**

## Objetivo

Criar autenticação de aplicações via API key, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Segurança e identidade") e `docs/AUTHENTICATION.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Segurança e identidade" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/AUTHENTICATION.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-010 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/AUTHENTICATION.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de autenticação/autorização (criação de usuário, papéis, validação de API key, criptografia/descriptografia de segredo), conforme docs/TESTING.md.

## Documentação afetada

`docs/AUTHENTICATION.md`, `docs/tasks/README.md`, `backend/app/auth/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/auth/api_keys.py`:
`generate_api_key()` (256 bits de entropia via `secrets.token_urlsafe`, prefixo
`cldk_`), `create_application(name)` (grava só o hash SHA-256 — sem PBKDF2, já
que a key nasce com alta entropia, diferente de senha de usuário; retorna o
texto plano uma única vez, na criação) e `authenticate_application(api_key)`.
3 testes unitários (geração) + 6 de integração real com o banco (criação,
nunca armazena texto plano, nome duplicado, autenticação correta/incorreta/
vazia). Suíte completa: 69/69 testes aprovados.
