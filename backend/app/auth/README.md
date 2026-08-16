# Autenticação e autorização

Documentação: docs/AUTHENTICATION.md. TASKs: TASK-009 a TASK-011.

Autenticação humana (usuário/senha, perfis ADMIN/USER) e autenticação de aplicações via API key.

- `password.py` (TASK-009) — hash/verificação de senha, PBKDF2-HMAC-SHA256 via
  `hashlib` (sem dependência nova), 600.000 iterações, salt aleatório.
- `users.py` (TASK-009) — `create_user()`/`authenticate_user()`. `VALID_ROLES`
  deriva de `Role` (TASK-010) — fonte única de verdade.
- `roles.py` (TASK-010) — `Role` (`ADMIN`/`USER`), `is_admin(role)`,
  `require_admin(role, details=None)` (levanta `ClaudiaoError` 2001/403 se não
  for admin). Opera sobre a string `role`, não sobre `User`, para não criar
  import circular com `users.py`.
- `api_keys.py` (TASK-011) — `generate_api_key()` (256 bits, prefixo `cldk_`),
  `create_application(name)` (retorna a key em texto plano só uma vez; grava
  hash SHA-256 simples — sem PBKDF2, a key já nasce com alta entropia),
  `authenticate_application(api_key)`.
- `crypto.py` (TASK-012) — `generate_key()`/`encrypt_secret()`/
  `decrypt_secret()`, usando `Fernet` (`cryptography`, DEC-007). Recebe a
  chave pronta; de onde ela vem é a TASK-013.
- `master_key.py` (TASK-013) — `load_or_create_master_key(path=None)`. Chave
  fora do PostgreSQL, em arquivo local (`CLAUDIAO_MASTER_KEY_PATH` se `path`
  não for informado); gera uma chave nova na primeira vez, reusa depois.
  Proteção de permissão do arquivo é melhor-esforço no Windows — lacuna
  conhecida, ver `docs/SECURITY.md`.

Testes em `tests/unit/test_password.py`, `tests/unit/test_roles.py`,
`tests/unit/test_api_keys.py`, `tests/unit/test_crypto.py`,
`tests/unit/test_master_key.py` (unitários, sem banco) e
`tests/integration/test_users_integration.py`,
`tests/integration/test_api_keys_integration.py` (integração real com o
PostgreSQL local; pulam automaticamente se o banco não estiver disponível).
