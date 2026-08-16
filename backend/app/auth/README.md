# Autenticação e autorização

Documentação: docs/AUTHENTICATION.md. TASKs: TASK-009 a TASK-011.

Autenticação humana (usuário/senha, perfis ADMIN/USER) e autenticação de aplicações via API key.

- `password.py` (TASK-009) — hash/verificação de senha, PBKDF2-HMAC-SHA256 via
  `hashlib` (sem dependência nova), 600.000 iterações, salt aleatório.
- `users.py` (TASK-009) — `create_user()`/`authenticate_user()`. `role` só como
  valor armazenado; regras de autorização por papel são TASK-010.

Testes em `tests/unit/test_password.py` (unitário, sem banco) e
`tests/integration/test_users_integration.py` (integração real com o
PostgreSQL local; pula automaticamente se o banco não estiver disponível).
