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

### Implementação (TASK-011)

`backend/app/auth/api_keys.py`:

- `generate_api_key()` — 256 bits de entropia (`secrets.token_urlsafe`), prefixo
  `cldk_` para reconhecimento visual.
- `create_application(name)` — grava na tabela `applications` (schema da
  TASK-004) só o **hash** da key (SHA-256 simples — diferente da senha de
  usuário, TASK-009: a key já nasce com alta entropia, gerada por máquina, não
  escolhida por humano, então não precisa de PBKDF2 lento nem salt). Retorna a
  key em texto plano **uma única vez**, no momento da criação — depois disso,
  não há como recuperá-la, só gerar uma nova.
- `authenticate_application(api_key)` — recalcula o hash e busca por
  igualdade; retorna `None` para key vazia ou desconhecida.

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

## Autorização por papel (TASK-010)

Implementado em `backend/app/auth/roles.py`:

- `Role` — `Enum` com `ADMIN`/`USER`, fonte única de verdade (o
  `VALID_ROLES` de `app.auth.users`, TASK-009, agora deriva dele).
- `is_admin(role)` — `True` só para `Role.ADMIN`; qualquer outro valor
  (incluindo papéis desconhecidos) é tratado como não-admin.
- `require_admin(role, details=None)` — levanta `ClaudiaoError` com o novo
  código `2001` (`FORBIDDEN_ADMIN_ONLY`, HTTP 403, faixa `AUTH` do catálogo de
  erros — TASK-007) se `role` não for `ADMIN`.

Opera sobre a string `role`, não sobre a classe `User` (TASK-009), para não
criar dependência circular entre os dois módulos. Ainda sem nenhum chamador
real (painel administrativo é TASK-115 em diante) — só a primitiva de
autorização, pronta para ser usada quando houver uma rota/ação que precise
dela.

## TASKs relacionadas

TASK-009 a TASK-011: autenticação de usuários, roles `ADMIN`/`USER`, autenticação de
aplicações via API key. Criptografia de segredos e chave mestra estão em
`SECURITY.md` (TASK-012, TASK-013).
