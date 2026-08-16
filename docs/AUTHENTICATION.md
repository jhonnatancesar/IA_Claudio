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

## Autenticação de usuários (TASK-009)

Implementado em `backend/app/auth/`:

- `password.py` — `hash_password()`/`verify_password()`. PBKDF2-HMAC-SHA256 via
  `hashlib` (sem dependência nova), 600.000 iterações, salt aleatório de 16
  bytes por senha, comparação em tempo constante.
- `users.py` — `create_user(username, password, role)` (grava na tabela `users`
  da TASK-004, com a senha já em hash) e `authenticate_user(username, password)`
  (retorna o usuário ou `None`, sem distinguir "usuário não existe" de "senha
  errada" na resposta). `role` aqui é só o valor gravado — **regras de
  autorização por papel são escopo da TASK-010**, não implementadas aqui.

## TASKs relacionadas

TASK-009 a TASK-011: autenticação de usuários, roles `ADMIN`/`USER`, autenticação de
aplicações via API key. Criptografia de segredos e chave mestra estão em
`SECURITY.md` (TASK-012, TASK-013).
