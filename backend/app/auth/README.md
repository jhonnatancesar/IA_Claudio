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

Testes em `tests/unit/test_password.py`, `tests/unit/test_roles.py` (unitários,
sem banco) e `tests/integration/test_users_integration.py` (integração real com
o PostgreSQL local; pula automaticamente se o banco não estiver disponível).
