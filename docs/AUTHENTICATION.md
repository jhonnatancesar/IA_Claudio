# Autenticação

Fonte: seções 24 e 31 da especificação mestre.

## Autenticação humana e perfis

Perfis: `ADMIN` e `USER`. A arquitetura suporta múltiplos usuários, embora
inicialmente exista apenas um.

- **USER**: chat, próprio histórico e própria memória; sem painel administrativo.
- **ADMIN**: gestão completa do sistema, usuários, API keys e configurações.
- Usuários diferentes mantêm memória e histórico separados por `user_id`.

## Autenticação de aplicações

Cada aplicação tem sua própria API key/token (ver `API.md` para o payload completo
enviado pela aplicação). A gestão de API keys pelo `ADMIN` é coberta em `PANEL.md`.

## TASKs relacionadas

TASK-009 a TASK-011: autenticação de usuários, roles `ADMIN`/`USER`, autenticação de
aplicações via API key. Criptografia de segredos e chave mestra estão em
`SECURITY.md` (TASK-012, TASK-013).
