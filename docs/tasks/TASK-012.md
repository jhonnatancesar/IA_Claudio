# TASK-012 — Implementar criptografia de segredos

Status: **Concluída em 2026-08-16**

## Objetivo

Implementar criptografia de segredos, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Segurança e identidade") e `docs/SECURITY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Segurança e identidade" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/SECURITY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-011 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/SECURITY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de autenticação/autorização (criação de usuário, papéis, validação de API key, criptografia/descriptografia de segredo), conforme docs/TESTING.md.

## Documentação afetada

`docs/SECURITY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (DEC-007),
`backend/app/auth/README.md`

## Encerramento

Concluída em 2026-08-16. Nova dependência: `cryptography` (DEC-007). Criado
`backend/app/auth/crypto.py`: `generate_key()`, `encrypt_secret(plaintext,
key)` (token autenticado, nunca determinístico), `decrypt_secret(token, key)`
(levanta `InvalidSecretError` para chave errada ou token adulterado). Recebe a
chave já pronta — de onde ela vem (arquivo protegido, fora do PostgreSQL) é
escopo da TASK-013, não implementado aqui. 8 testes unitários novos (roundtrip,
plaintext vazio, não-determinismo, chave errada, token adulterado/inválido).
Suíte completa: 77/77 testes aprovados.
