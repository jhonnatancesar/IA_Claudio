"""Criação e autenticação de usuários (TASK-009).

`role` aqui só é validado e armazenado na tabela `users` (schema da TASK-004,
`ADMIN`/`USER` — seção 31 da especificação). Regras de autorização por papel (o
que cada papel pode fazer) são `app.auth.roles` (TASK-010).
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import psycopg

from app.auth.password import hash_password, verify_password
from app.auth.roles import Role
from app.db.connection import connect

VALID_ROLES = tuple(role.value for role in Role)


class UserAlreadyExistsError(ValueError):
    """Levantado ao tentar criar um usuário com um `username` já existente."""


class InvalidRoleError(ValueError):
    """Levantado quando `role` não é `ADMIN` nem `USER`."""


@dataclass(frozen=True)
class User:
    id: UUID
    username: str
    role: str


def create_user(username: str, password: str, role: str) -> User:
    """Cria um usuário novo, com a senha já em hash (nunca em texto plano no
    banco). Levanta `InvalidRoleError` para papel desconhecido e
    `UserAlreadyExistsError` para `username` duplicado."""
    if role not in VALID_ROLES:
        raise InvalidRoleError(f"papel inválido: {role!r} (use ADMIN ou USER)")
    if not username or not username.strip():
        raise ValueError("username não pode ser vazio")

    password_hash = hash_password(password)
    with connect() as conn:
        try:
            row = conn.execute(
                "INSERT INTO users (username, password_hash, role) "
                "VALUES (%s, %s, %s) RETURNING id, username, role",
                (username, password_hash, role),
            ).fetchone()
        except psycopg.errors.UniqueViolation as exc:
            raise UserAlreadyExistsError(f"usuário já existe: {username!r}") from exc

    user_id, db_username, db_role = row
    return User(id=user_id, username=db_username, role=db_role)


def authenticate_user(username: str, password: str) -> User | None:
    """Autentica por usuário/senha. Retorna `None` para usuário inexistente ou
    senha incorreta — sem distinguir os dois casos na resposta (evita vazar
    quais usernames existem)."""
    with connect() as conn:
        row = conn.execute(
            "SELECT id, username, role, password_hash FROM users WHERE username = %s",
            (username,),
        ).fetchone()

    if row is None:
        return None
    user_id, db_username, role, password_hash = row
    if not verify_password(password, password_hash):
        return None
    return User(id=user_id, username=db_username, role=role)
